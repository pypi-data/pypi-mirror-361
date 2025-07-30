# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of AccidentallyTheCables Utility Kit,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import re
import typing
from pathlib import Path
from json import loads as json_parse
from json import dumps as json_dump
from yaml import dump as yaml_dump
from yaml import safe_load as yaml_parse
from tomlkit import parse as toml_parse
from tomlkit import dumps as toml_dump

def toml_parser(content:str) -> dict[typing.Any,typing.Any]:
    """TOML Parse and unwrap
    @param str \c content Raw TOML string
    @retval dict[Any,Any] Dictionary from TOML
    """
    return toml_parse(content).unwrap()

def scan_dir(target_path:Path,
                callback:typing.Callable[[Path,dict[str,typing.Any]],None],
                callback_data:dict[str,typing.Any],
                exclude_dirs:typing.Optional[list[re.Pattern]] = None,
                exclude_files:typing.Optional[list[re.Pattern]] = None,
                include_files:typing.Optional[list[re.Pattern]] = None
            ) -> None:
    """Scan A Directory, and Execute callback on discovered files, that do not match the exclusions
    @param Path \c target_path Path to Scan for Files
    @param typing.Callable[[Path,dict[str,Any]],None] \c callback Callback function to execute on each file
    @param dict[str,Any] \c callback_data Data to pass to the callback function
    @param list[re.Pattern] \c exclude_dirs (optional) Regex Compiled list of directory patterns to exclude
    @param list[re.Pattern] \c exclude_files (optional) Regex Compiled list of file patterns to exclude
    @param list[re.Pattern] \c include_files (optional) Regex Compiled list of file patterns to include
    """
    files:typing.Generator[Path, None, None] = target_path.glob("*")
    skip:bool = False
    for file in files:
        file_path:Path = Path(file)
        if file_path.is_dir():
            skip = False
            if exclude_dirs is not None:
                for reg in exclude_dirs:
                    if reg.match(file_path.as_posix()):
                        skip = True
                        break
            if not skip:
                scan_dir(target_path=file_path,callback=callback,callback_data=callback_data,exclude_dirs=exclude_dirs,exclude_files=exclude_files,include_files=include_files)
        if file_path.is_file():
            if include_files is not None:
                skip = True
                for reg in include_files:
                    if reg.match(file_path.name):
                        skip = False
                        break
            if exclude_files is not None:
                skip = False
                for reg in exclude_files:
                    if reg.match(file_path.name):
                        skip = True
                        break
            if not skip:
                callback(file_path,callback_data)

def dump_sstr(content:typing.Union[list[typing.Any],dict[typing.Any,typing.Any]],output_type:str,**kwargs:typing.Any) -> str:
    """Dump Structured Data to String, Selectable Output Type.
    @param dict[Any,Any] \c content Content to dump
    @param str \c output_type Output Type, Allowed: yaml, json, toml
    @param kwargs \c kwargs kwargs passed to selected data dumper
    @retval str Structured Data as a string
    @exception LookupError Raised When Unable to Locate a a parser by file type, or the overridden type is invalid
    @exception RuntimeError Raised When Unable to Parse the specified file using the specified type (automatically, or overridden)

    kwargs:
        See the related kwargs for:
            json.dumps
            yaml.dump
            tomlkit.dumps
    """
    if output_type not in FileUtilConfig.OUTPUT_TYPE_MAP.keys():
        raise LookupError("Output Type is not valid",output_type)
    dumper:typing.Callable = FileUtilConfig.OUTPUT_TYPE_MAP[output_type]
    try:
        output:str = dumper(content,*kwargs)
    except BaseException as e:
        raise RuntimeError("Failed to output content",'.'.join([dumper.__class__.__name__,dumper.__name__]),e) from e
    return output

def load_sstr(raw_data:str,content_type:str) -> dict[typing.Any,typing.Any]:
    """Load Structured Data Content, based on content_type
    @param str \c raw_data Raw Content
    @param str \c content_type Render for Content Type, Allowed: yaml, json, toml
    @retval dict[Any,Any] Dictionary of Structured Data
    """
    parser:typing.Callable
    if content_type not in FileUtilConfig.TYPE_OVERRIDE_MAP.keys():
        raise LookupError("Override Type is not valid",content_type)
    parser = FileUtilConfig.TYPE_OVERRIDE_MAP[content_type]
    loaded_config:dict[typing.Any,typing.Any] = parser(raw_data)
    return loaded_config

def load_sfile(target_file:Path,override_type:str = "auto") -> dict[typing.Any,typing.Any]:
    """Load Structured Data File, automatically determining data by file extension
    @param Path \c target_file Configuration File to Load
    @param str \c override_type Input Type Override, Allowed: yaml, json, toml, auto. Default: auto
    @retval dict[Any,Any] Dictionary of Structured Data
    @exception LookupError Raised When Unable to Locate a a parser by file type, or the overridden type is invalid
    @exception RuntimeError Raised When Unable to Parse the specified file using the specified type (automatically, or overridden)

    Accepted File Extensions:
        YAML: .yaml, .yml
        JSON: .json
        TOML: .toml
    """
    if not target_file.exists():
        raise FileNotFoundError("Cannot Locate File",target_file.as_posix())
    content_type:str = override_type
    if override_type == "auto":
        if target_file.suffix not in FileUtilConfig.FILE_TYPE_MAP.keys():
            raise LookupError("No Parser located for file type",target_file.suffix)
        content_type = re.sub(r'^\.','',target_file.suffix)
    try:
        with open(target_file,"r",encoding="utf-8") as f:
            loaded_config:dict[typing.Any,typing.Any] = load_sstr(f.read(),content_type)
            return loaded_config
    except BaseException as e:
        raise RuntimeError("Failed to Parse file",target_file.as_posix(),e) from e

def find_config_file(service:str,config_name:str) -> typing.Union[Path,None]:
    """Search for Configuration File in common places

    Uses FileUtil.CONFIG_SCAN_BASE_PATHS and FileUtil.CONFIG_SCAN_FILE_EXTS to search for files

    Scans as: <scan path>/<service>/<config_name>.<scan ext>

    @param str \c service Name of Service to Use (EX: myservice)
    @param str \c config_name Name of Configration File to find
    @retval Union[Path,None] Located configuration path, or None if not found
    """
    for p in FileUtilConfig.CONFIG_SCAN_BASE_PATHS:
        check_svcpath:Path = p.expanduser().resolve().joinpath(service).resolve()
        if not check_svcpath.is_dir():
            continue
        for ext in FileUtilConfig.CONFIG_SCAN_FILE_EXTS:
            check_file:Path = check_svcpath.joinpath(f"{config_name}.{ext}").resolve()
            if check_file.is_file():
                return check_file
    return None

def add_config_search_path(path:Path) -> None:
    """Add Basepath to Config Search (EX /usr/local/)
    @param Path \c path Basepath to add for scanning
    @retval None Nothing
    """
    if path not in FileUtilConfig.CONFIG_SCAN_BASE_PATHS:
        FileUtilConfig.CONFIG_SCAN_BASE_PATHS.append(path)

# pylint: disable=useless-return
def remove_config_search_path(path:Path) -> None:
    """Remove Basepath from Config Search
    @param Path \c path Basepath to attempt to remove
    @retval None Nothing
    """
    try:
        FileUtilConfig.CONFIG_SCAN_BASE_PATHS.pop(FileUtilConfig.CONFIG_SCAN_BASE_PATHS.index(path))
    except ValueError:
        return
# pylint: enable=useless-return

def add_config_search_file_ext(ext:str) -> None:
    """Add File Extension to Config Search (EX conf)
    @param str \c ext File Extension to add for scanning
    @retval None Nothing
    """
    if ext not in FileUtilConfig.CONFIG_SCAN_FILE_EXTS:
        FileUtilConfig.CONFIG_SCAN_FILE_EXTS.append(ext)

# pylint: disable=useless-return
def remove_config_search_file_ext(ext:str) -> None:
    """Remove File Extension from Config Search
    @param str \c ext File Extension to attempt to remove
    @retval None Nothing
    """
    try:
        FileUtilConfig.CONFIG_SCAN_FILE_EXTS.pop(FileUtilConfig.CONFIG_SCAN_FILE_EXTS.index(ext))
    except ValueError:
        return
# pylint: enable=useless-return

class FileUtilConfig:
    """Utility Functions
    """

    FILE_TYPE_MAP:dict[str,typing.Callable] = {
        ".yml": yaml_parse,
        ".yaml": yaml_parse,
        ".json": json_parse,
        ".toml": toml_parser
    }
    TYPE_OVERRIDE_MAP:dict[str,typing.Callable] = {
        "yaml": yaml_parse,
        "json": json_parse,
        "toml": toml_parser
    }
    OUTPUT_TYPE_MAP:dict[str,typing.Callable] = {
        "yaml": yaml_dump,
        "json": json_dump,
        "toml": toml_dump
    }

    CONFIG_SCAN_BASE_PATHS:list[Path] = [
        Path("~/.local/"),
        Path("/etc/")
    ]

    CONFIG_SCAN_FILE_EXTS:list[str] = [
        "toml",
        "yaml",
        "json"
    ]

#### CHECKSUM 11ff3f9f478ea8034ed19b53026b88e14e66cb5e5dd9dca1a74a46e00251be89
