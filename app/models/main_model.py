# main_model.py
import yaml
import os
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
)
from .foxglove_ws_model import FoxgloveWsModel
from .ros2_launch_container_model import ROS2LaunchContainerModel
from .settings_cfg_model import (
    OtherSettingsCfgModel,
    NtripSettingsCfgModel,
)

from app.utils.logger import logger

class MainModel(QObject):
    
    signal_on_waypoints_loaded = pyqtSignal(str, dict) # (file_path, waypoints)
    signal_on_params_loaded = pyqtSignal(str, dict) # (file_path, params)
    
    signal_on_settings_param_loaded = pyqtSignal(str, dict) # (file_path, params)
    
    """
    MainModel aggregates all application models.
    """
    def __init__(self, config):
        """
        Initializes MainModel with the provided configuration.
        """
        super().__init__()
        self._config = config
        self._foxglove_ws_model = FoxgloveWsModel.get_instance(
            config=self._config,
        )
        self._ros2_launch_container_model = ROS2LaunchContainerModel.get_instance(
            config=self._config,
        )
        # self._ros2_launch_container_model.create_all_launch_containers()
        
        # self.ntrip_params_cfg_model = NTRIPParamsCfgModel.get_instance(
        #     config=self._config,
        # )
        self.ntrip_settings_cfg_model = NtripSettingsCfgModel.get_instance(
            config=self._config,
        )
        
        self.other_settings_cfg_model = OtherSettingsCfgModel.get_instance(
            config=self._config,
        )
        
    @property
    def foxglove_ws_model(self):
        """
        Returns the Foxglove WebSocket model.
        """
        return self._foxglove_ws_model
    
    @property
    def ros2_launch_container_model(self):
        """
        Returns the ROS2 Launch Container model.
        """
        return self._ros2_launch_container_model
    
    def save_yaml_waypoints(self, waypoints: dict, file_path: str):
        """
        Saves the given waypoints to a YAML file.
        """
        with open(file_path, 'w') as file:
            yaml.dump(waypoints, file)
            
    def _hard_load_yaml_file(self, source_path: str, target_path: str) -> dict:
        """
        Common function to load YAML data from source_path and save to target_path.
        """
        try:
            # Read selected file
            with open(source_path, 'r') as file:
                yaml_data = yaml.safe_load(file)

            # Check if target file exists
            if not os.path.exists(target_path):
                with open(target_path, 'w') as file:
                    yaml.dump(yaml_data, file)
            else:
                with open(target_path, 'r+') as file:
                    existing_data = yaml.safe_load(file)
                    if existing_data != yaml_data:
                        # Update the file with new data
                        file.seek(0)
                        yaml.dump(yaml_data, file)
                        file.truncate()

            return yaml_data

        except Exception as e:
            logger.error(f"Error loading YAML file {source_path}: {e}")
            return None

    def hard_load_yaml_waypoints_file(self, file_path: str):
        """
        Loads waypoints from a YAML file.
        """
        target_wp_file_path = self._config['mowbot_legacy_data_path'] + "/" + self._config["waypoints_file"]
        waypoints = self._hard_load_yaml_file(file_path, target_wp_file_path)
        file_name = os.path.basename(file_path)
        # Check if the file name is valid
        if waypoints:
            self.signal_on_waypoints_loaded.emit(
                file_name, waypoints
            )

    def hard_load_yaml_nav_params_file(self, file_path: str):
        """
        Loads parameters from a YAML file.
        """
        target_params_file_path = self._config['mowbot_legacy_data_path'] + "/" + self._config["nav_params_file"]
        params = self._hard_load_yaml_file(file_path, target_params_file_path)
        file_name = os.path.basename(file_path)
        if params:
            self.signal_on_params_loaded.emit(
                file_name, params
            )        
            
    def soft_load_yaml_nav_param_settings_file(self, file_path: str):
        
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data
    
    def save_yaml_param_settings_file(self, file_path: str, yaml_data: dict):
        # check if file path has .yaml extension
        if not file_path.endswith('.yaml'):
            file_path += '.yaml'
        with open(file_path, 'w') as file:
            yaml.dump(yaml_data, file)
        logger.info(f"YAML file saved to {file_path}")
        

