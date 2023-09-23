import os
import pprint
import re
import shutil
import sys
from pathlib import Path

from typing import List, Dict, Tuple, Optional, Any, Union

known_file_extensions = set()
unknown_file_extensions = set()

file_types = {
    'AMR': 'audio',
    'AVI': 'video',
    'DOC': 'documents',
    'DOCX': 'documents',
    'GZ': 'archives',
    'JPEG': 'images',
    'JPG': 'images',
    'MKV': 'video',
    'MOV': 'video',
    'MP3': 'audio',
    'MP4': 'video',
    'OGG': 'audio',
    'PDF': 'documents',
    'PNG': 'images',
    'PPTX': 'documents',
    'SVG': 'images',
    'TAR': 'archives',
    'TXT': 'documents',
    'WAV': 'audio',
    'XLSX': 'documents',
    'ZIP': 'archives'
}

translate_map = {
    ord('А'): 'A', ord('Б'): 'B', ord('В'): 'V', ord('Г'): 'H', ord('Ґ'): 'G',
    ord('Д'): 'D', ord('Е'): 'E', ord('Є'): 'YE', ord('Ж'): 'ZH', ord('З'): 'Z',
    ord('И'): 'Y', ord('І'): 'I', ord('Ї'): 'YI', ord('К'): 'K', ord('Л'): 'L',
    ord('М'): 'M', ord('Н'): 'N', ord('О'): 'O', ord('П'): 'P', ord('Р'): 'R',
    ord('С'): 'S', ord('Т'): 'T', ord('У'): 'U', ord('Ф'): 'F', ord('Х'): 'KH',
    ord('Ц'): 'TS', ord('Ч'): 'CH', ord('Ш'): 'SH', ord('Щ'): 'SCH',
    ord('Ь'): '', ord('Ю'): 'YU', ord('Я'): 'YA',

    ord('а'): 'a', ord('б'): 'b', ord('в'): 'v', ord('г'): 'g', ord('ґ'): 'g',
    ord('д'): 'd', ord('е'): 'e', ord('є'): 'ye', ord('ж'): 'zh', ord('з'): 'z',
    ord('и'): 'i', ord('і'): 'i', ord('ї'): 'yi', ord('к'): 'k', ord('л'): 'l',
    ord('м'): 'm', ord('н'): 'n', ord('о'): 'o', ord('п'): 'p', ord('р'): 'r',
    ord('с'): 's', ord('т'): 't', ord('у'): 'u', ord('ф'): 'f', ord('х'): 'kh',
    ord('ц'): 'ts', ord('ч'): 'ch', ord('ш'): 'sh', ord('щ'): 'sch',
    ord('ь'): '', ord('ю'): 'yu', ord('я'): 'ya'
}


def __normalize(file_name: str) -> str:
    """
    Method normalizes text, replacing all special symbols with underscore except
    digits, underscores and the last dot in the 'text'.
    :param file_name: The file name without extension that should be normalized.
    :return: Normalized text.
    """
    file_name = file_name.translate(translate_map)
    return re.sub(r'\W', '_', file_name)


def __unpack_archive(archive_path: Path, extract_dir: str) -> None:
    """
    Method that unpacks archive into specific folder.
    :param archive_path: Path to archive that should be unpacked.
    :param extract_dir: Path to directory into which the archive should be unpacked.
    :return: None.
    """
    extract_dir_path: Path = Path(extract_dir)
    if not extract_dir_path.exists():
        extract_dir_path.mkdir()
    archive_folder, _ = __get_file_name_and_extension(
        file_obj=archive_path)
    extract_dir += f"/{archive_folder}"
    shutil.unpack_archive(filename=str(archive_path.resolve()), extract_dir=extract_dir)
    os.remove(path=str(archive_path.resolve()))


def __get_unpacked_files(folder_path: str) -> List[str]:
    """
    Method gets the list of files (ignoring folders) that are present in the folder
    after unpacking archive.
    :param folder_path: Path to folder with extracted files from the archive.
    :return: The list of files's names.
    """
    p = Path(folder_path)
    subtree_iter = p.glob("**/*")
    return [file_obj.name for file_obj in subtree_iter if file_obj.is_file()]


def __fill_file_extensions_into_set(folder_name: str, file_ext: str) -> None:
    """
    Method fills the sets defined in a global scope with the files's extensions
    that are known and unknown (based on the dictionary 'files_types').
    :param folder_name: The name of folder based on file type (file_ext).
    :param file_ext: The file extension.
    :return: None.
    """
    if folder_name == "others":
        unknown_file_extensions.add(file_ext)
    else:
        known_file_extensions.add(file_ext)


def __get_file_name_and_extension(file_obj: Path) -> Tuple[str, Union[str, Any]]:
    """
    Method gets the name of file and extension.
    :param file_obj: Path object of a file.
    :return: Tuple of the file name and file extension.
    """
    file_name: str = file_obj.name
    file_info: list = file_name.split(".")
    file_name: str = ".".join(file_info[:-1]) if len(file_info) >= 2 else ".".join(
        file_info)
    file_ext = file_info[-1] if len(file_info) >= 2 else ""
    return file_name, file_ext


def __get_file_info_base_on_file_type(file_obj: Path) -> \
        Tuple[str, Optional[Any], Union[str, Any]]:
    """
    Method defines the name of folder based on file type (file extension).
    :param file_obj: Path object of a file that should be analyzed.
    :return: File name, file extension and folder name based on file type.
    """
    file_name, file_ext = __get_file_name_and_extension(file_obj=file_obj)
    folder_name = file_types.get(file_ext.upper(), "others")
    __fill_file_extensions_into_set(folder_name=folder_name, file_ext=file_ext)
    return file_name, file_ext, folder_name


def __get_normalized_full_file_name(file_name: str, file_ext: str) -> str:
    """
    Method normalizes the file name and add file extension to generate a full
    normalized file name.
    :param file_name: File name without extension.
    :param file_ext: File extension.
    :return: The full normalized file name.
    """
    normalized_file_name = __normalize(file_name)
    if file_ext:
        return f"{normalized_file_name}.{file_ext}"
    return normalized_file_name


def __move_and_rename_file(file_obj: Path, new_folder_name: str) -> None:
    """
    Method moves file into the appropriate folder and normalizes the file name with
    the method __normalize(file_name).
    :param file_obj: Path object of a file that should be renamed and moved.
    :param new_folder_name: The name of folder in which the file should be transferred.
    :return: None.
    """
    folder_path: Path = Path(new_folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    file_name, file_ext = __get_file_name_and_extension(file_obj=file_obj)
    normalized_full_file_name = __get_normalized_full_file_name(file_name=file_name,
                                                                file_ext=file_ext)
    new_file_path = f"{new_folder_name}/{normalized_full_file_name}"
    file_obj.rename(Path(new_file_path))


def __delete_folder(folder_path: str) -> None:
    """
    The method deletes the files one by one from the bottom level to top in case if the
    directory is empty.
    :param folder_path: The path for the parent folder.
    :return: None.
    """
    folder_path_obj = Path(folder_path)
    subtree_iter = folder_path_obj.glob("**")
    for sub_folder_path in sorted(list(subtree_iter), reverse=True):
        if not os.listdir(sub_folder_path):
            os.rmdir(sub_folder_path)


def __sort_folder(folder_path: str) -> Dict[str, list]:
    """
    Method analyzes folder structure and sort files inside it. Based on this method,
    a new structure of folders will be created with files, sorted by their types.
    :param folder_path: Path to folder that should be restructured.
    :return: Dictionary with list of files and their extensions.
    """
    result_dict = dict()
    p = Path(folder_path)
    subtree_iter = p.glob("**/*")
    for entity in subtree_iter:
        if entity.is_file():
            file_name, file_ext, new_folder_name = __get_file_info_base_on_file_type(
                file_obj=entity)
            normalized_full_file_name = __get_normalized_full_file_name(file_name=file_name,
                                                                        file_ext=file_ext)
            if new_folder_name != "archives":
                if new_folder_name in result_dict:
                    result_dict[new_folder_name].append(normalized_full_file_name)
                else:
                    result_dict[new_folder_name] = [normalized_full_file_name]
                __move_and_rename_file(entity, new_folder_name)
            else:
                __unpack_archive(archive_path=entity, extract_dir=new_folder_name)
    result_dict["archives"] = __get_unpacked_files("archives")
    result_dict["known_file_extensions"] = list(known_file_extensions)
    result_dict["unknown_file_extensions"] = list(unknown_file_extensions)
    __delete_folder(folder_path=folder_path)
    return result_dict


def sort_folder():
    if len(sys.argv) >= 2:
        folder_name = sys.argv[1]
    else:
        raise Exception("Pass the folder name into command line as an argument")
    new_files_structure = __sort_folder(folder_path=folder_name)
    print("Result after restructuring folder '{}' with files: \n".format(folder_name))
    pprint.pprint(new_files_structure)
