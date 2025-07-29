import logging
from pathlib import Path



class ResourceFinder:

    @property
    def logger(self) -> logging.Logger:
        return self._logger


    def __init__(self, top_rep: Path, bottom_rep: Path):

        #self._logger = logging.getLogger(self.__class__.__name__)

        from mqtt_device.common.common_log import create_logger
        self._logger = create_logger(self)

        self._top_rep = Path(top_rep)
        self._bottom_rep = Path(bottom_rep)

        if not self._top_rep.exists():
            raise BaseException("Directory from_rep : '{}' does not exist".format(top_rep))

        if not self._bottom_rep.exists():
            raise BaseException("Directory root : '{}' does not exist".format(bottom_rep))



    def find_resource(self, resource_name: str):

        return self._find_resource(self._bottom_rep, Path(resource_name))


    def _find_resource(self, path:Path, resource_rel_path: Path):

        resource_dir = path/'resources'

        self.logger.debug("Find 'resources' directory in '{}'".format(resource_dir))

        #on cherche a trouver un repertoire de resource dans le path courant
        if resource_dir.exists():

            self.logger.debug("'resources' directory founded at '{}'".format(resource_dir))

            resource_path = resource_dir/resource_rel_path

            if resource_path.exists():
                return resource_path



        #sinon on remonte dans le parent et on fait la meme recherche
        parent = path.parent

        if parent != self._top_rep and parent != path:

            #on s'arrete au dossier root de la librairie
            return self._find_resource(parent, resource_rel_path)
        else:

            print("On est a la racine : {}".format(self._top_rep))
            return None
