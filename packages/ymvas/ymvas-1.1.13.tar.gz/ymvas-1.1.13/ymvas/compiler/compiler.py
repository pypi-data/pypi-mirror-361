from os.path import join, exists, dirname, basename, isdir, relpath
from pathlib import Path
import os, json, shutil, yaml, subprocess
from os import walk, sep, remove

from functools   import lru_cache
from ..settings  import Settings
from .change import Change

class Compiler:

    def __init__( self, stg:Settings ):
        self.settings = stg

        self.modules = [ 
            m.name for m in stg.get_modules().values() if not m.root 
        ]

    @property
    def _git(self):
        return (
            f"git --git-dir='{self.settings.git}' "
            f" --work-tree='{self.settings.root}' "
        )
    
    @property
    @lru_cache(maxsize=None)
    def commit(self):
        return os.popen(
            f"{self._git} rev-parse HEAD"
        ).read().strip()
    
    @property
    @lru_cache(maxsize=None)
    def first_commit(self):
        return os.popen(
            f"{self._git} rev-list --max-parents=0 HEAD"  
        ).read().strip()
    
    @property
    def prev_config_exists(self):
        return exists(join(self.destination,'config.json'))

    @property
    @lru_cache(maxsize=None)
    def config(self):
        fp = join(self.destination,'config.json')
        if not exists(fp):
            return {}
        with open(fp) as f:
            return json.loads(f.read())
        return {}
    
    @lru_cache(maxsize=None)
    def is_uncommited(self):
        return os.popen(f"{self._git} status -s").read().strip() != ""
    
    def is_older(self,o_com,n_com):
        if o_com == self.first_commit:
            return False
        try:
            subprocess.run([
                "git", 
                f"--git-dir='{self.settings.git}'",
                'merge-base', 
                '--is-ancestor', 
                o_com, 
                n_com
               ],
               check=True,
               capture_output = True,
               text=True 
            )
            return True
        except subprocess.CalledProcessError as e:
            return False
    
    def get_changes(self,c_old,c_new):
        tracked = " ".join([
          self.settings.d_endpoints ,
          self.settings.d_settings
        ])
        
        # command changes commited
        cmd = (
           f"{self._git} --no-pager diff --name-status "
           f"{c_old} {c_new} -- {tracked}"
        )
        com = os.popen( cmd ).read().strip()
        
        cmd = f"{self._git} --no-pager status -s {tracked}"
        mod = os.popen( cmd ).read().strip()
        
        # get all changes in one list
        data    = mod.split("\n") + com.split("\n")
        changes = []

        for f in data:
            f = f.strip().replace("\t"," ")
            file  = " ".join(f.split(' ')[1:])

            if '"' in f or "'" in f:
                continue # skip strange files
            
            # handle rename 
            if f.upper().startswith("R"):
                fxf  = file.split('->')
                file = fxf[-1].strip()

                changes.append(Change(
                    self.settings, fxf[-1].strip(), Change.DELETED 
                ))
                changes.append(Change(
                    self.settings, fxf[0].strip() , Change.UPDATED
                ))

                continue

            if f.upper().startswith("D"):
                changes.append(Change( 
                    self.settings, file , Change.DELETED 
                ))
                continue

            changes.append(Change( self.settings, file , Change.UPDATED ))
        

        return changes
    
            
    def get_end_conf(self):
        if not exists(self.settings.f_settings_endpoints):
            return {}
        with open(self.settings.f_settings_endpoints,'r') as f:
            data = yaml.safe_load(f.read())
            if isinstance(data,dict):
                return data
        return {}


  
    def get_settings_changes(self,conf_e,conf_o):
        files = conf_o.get("files",{})
        endpoints_p = self.settings.relpath(
            self.settings.d_endpoints
        )
        
        changes = []
        for e, cnf_e in conf_e.items():
            old = files.get(e,{})

            if json.dumps(cnf_e) == json.dumps(old):
                continue

            file = join( endpoints_p, e )
            changes.append(Change(self.settings, file ,Change.UPDATED))
         
        return changes


    def clean(self , destination ):
        if not exists(destination):
            return True

        if not self.settings.is_main:
            self.settings.log(f"deleted all previous data")
            shutil.rmtree(destination)
            return True

        def _loop():
            for r,_,files in walk( destination ):
                for f in files:
                    yield join(r,f)

        for f in _loop():
            rf = relpath(f, destination )
            dd = rf.split( sep )
            if dd[0] in self.modules:
                continue
            self.settings.log(f"removed {rf}")
            remove(f)


        return True


    def run( self , compile_dir ):
        self.destination = compile_dir 
        
        # setup variables *_o => previous data
        conf_o = self.config
        comm_o = conf_o.get('commit',self.first_commit)

        from ..__init__ import __version__
        conf_n = {
            'commit': self.commit,
            'version' :__version__
        }
       
        # store modules folders so we don't overwrite them
        if self.settings.is_main:
            conf_n['modules'] = self.modules
        
        if conf_o.get('version','0') != __version__:
            self.settings.log('mismatch of version recompile files')
            comm_o = self.first_commit
            conf_o = {}
            self.clean( compile_dir )

        # drop all files and start from scratch
        # looks like local compiler
        if self.is_uncommited():
            self.settings.log(f"Looks like working on local")
            comm_o = self.first_commit # set commit as first
            conf_o = {}
            self.clean( compile_dir )
    

        self.settings.log(
            f"Different commit? {self.commit != comm_o}"
            f" | {self.commit} == {comm_o}"
        )

        # no changes between commits
        if self.commit == comm_o:
            self.settings.log(f"No changes detected!")
            return conf_o

        
        # drop all files and start from scratch
        # looks like forced commit
        if not self.is_older(comm_o,self.commit):
            comm_o = self.first_commit # set commit as first
            conf_o = {} 
            self.clean( compile_dir )

   
        os.makedirs( compile_dir , exist_ok = True )
        # START THE COMPILATION PROCESS

        
        changes = self.get_changes(comm_o,self.commit)    
        if len(changes) == 0:
            self.settings.log(f"No changes detected!")
            return conf_o
            
        # sync and rm outdated, and get endpoints settings
        nchanges = []
        end_conf = {}
        avatar = None
        
        for c in changes:
            self.settings.log(c.fullpath)
            if c.is_dir: continue

            c.sync(
                self.destination,
                conf_o
            )

            if c.is_avatar:
                avatar = c
                continue
            
            if c.is_endpoints_setting:
                end_conf = self.get_end_conf()
            

            if c.is_outdated() and c.is_endpoint:
                c.rm()
                continue
            elif not c.is_endpoint:
                continue
            nchanges.append(c)
        
        # check if settings are modified if so recompile the files changed
        schanges = self.get_settings_changes(end_conf,conf_o)
        for c in schanges:
            c.sync(
                self.destination,
                conf_o
            )

            _cnf = end_conf.get(c.cnf_name,{})

            self.settings.log(
                f"settings changes = {c.cnf_name} => "
                f"{_cnf}"
            )

            c.format = _cnf.get("format" ,None)
            c.into   = _cnf.get("into"   ,None)

            _exists = False
            for i, gc in enumerate(nchanges):
                if c.cnf_name == gc.cnf_name:
                    _exists = True
                    nchanges[i] = c
                    break

            if _exists:
                continue

            nchanges.append(c)
        
        conf_n['files'] = {}
        for c in nchanges:
            c.create()
            name, data = c.config()
            conf_n['files'][name] = data
 
        # get avatar
        if self.settings.is_main and avatar is not None:
            ovatar = conf_o.get('avatar',None)
            if ovatar != None:
                remove(join(destination,ovatar))
            avatar.create()
            conf_n['avatar'] = avatar.cnf_name

        with open(join(self.destination,'config.json'),'w') as f:
            f.write(json.dumps(conf_n, indent = 4))

        # print complie data
        self.settings.log(f"Final config : {json.dumps(conf_n,indent = 1)}")
        return conf_n

