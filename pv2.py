#!/usr/bin/python3

import re
import os


# this is a hardcoded file for testing purposes only
FILENAME = "test-files/proc_some-module.adoc"


class Colors:
    '''
    defines colors to use in the command line output
    '''
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Regex:
    '''
    defines regular expresiions for the checks
    '''
    VANILLA_XREF = re.compile(r'<<.*>>')
    PSEUDO_VANILLA_XREF = re.compile(r'<<((.*) (.*))*>>')
    MULTI_LINE_COMMENT = re.compile(r'(/{4,})(.*\n)*?(/{4,})')
    SINGLE_LINE_COMMENT = re.compile(r'(?<!//)(?<!/)//(?!//).*\n?')
    EMPTY_LINE_AFTER_ABSTRACT = re.compile(r'\[role="_abstract"]\n(?=\n)')
    FIRST_PARA = re.compile(r'(?<!\n\n)\[role="_abstract"]\n(?!\n)')
    NO_EMPTY_LINE_BEFORE_ABSTRACT = re.compile(r'(?<!\n\n)\[role="_abstract"]')
    COMMENT_AFTER_ABSTRACT = re.compile(r'\[role="_abstract"]\n(?=\//|(/{4,})(.*\n)*?(/{4,}))')
    VAR_IN_TITLE = re.compile(r'(?<!\=)=\s.*{.*}.*')
    INLINE_ANCHOR = re.compile(r'=.*\[\[.*\]\]')
    UI_MACROS = re.compile(r'btn:\[.*\]|menu:.*\]|kbd:.*\]')
    HTML_MARKUP = re.compile(r'<.*>.*<\/.*>|<.*>\n.*\n</.*>')
    CODE_BLOCK = re.compile(r'(?<=\.\.\.\.\n)((.*)\n)*(?=\.\.\.\.)|(?<=----\n)((.*)\n)*(?=----)')
    HUMAN_READABLE_LABEL_XREF = re.compile(r'xref:.*\[]')
    NESTED_ASSEMBLY = re.compile(r'include.*assembly_([a-z|0-9|A-Z|\-|_]+)\.adoc(\[.*\])')
    NESTED_MODULES = re.compile(r'include.*(proc|con|ref)_([a-z|0-9|A-Z|\-|_]+)\.adoc(\[.*\])')
    RELATED_INFO = re.compile(r'= Related information|.Related information', re.IGNORECASE)
    ADDITIONAL_RES = re.compile(r'= Additional resources|\.Additional resources', re.IGNORECASE)
    ADD_RES_ASSEMBLY = re.compile(r'== Additional resources', re.IGNORECASE)
    ADD_RES_MODULE = re.compile(r'\.Additional resources', re.IGNORECASE)
    EMPTY_LINE_AFTER_ADD_RES_TAG = re.compile(r'\[role="_additional-resources"]\n(?=\n)')
    COMMENT_AFTER_ADD_RES_TAG = re.compile(r'\[role="_additional-resources"]\n(?=\//|(/{4,})(.*\n)*?(/{4,}))')
    EMPTY_LINE_AFTER_ADD_RES_HEADER = re.compile(r'== Additional resources\s\n|\.Additional resources\s\n', re.IGNORECASE)
    COMMENT_AFTER_ADD_RES_HEADER = re.compile(r'\.Additional resources\s(?=\//|(/{4,})(.*\n)*?(/{4,}))|== Additional resources\s(?=\//|(/{4,})(.*\n)*?(/{4,}))', re.IGNORECASE)


class FileType:
    '''
    defines strings for finding out fily type
    '''
    ASSEMBLY = re.compile(r'assembly_.*\.adoc')
    CONCEPT = re.compile(r'con_.*\.adoc')
    PROCEDURE = re.compile(r'proc_.*\.adoc')
    REFERENCE = re.compile(r'ref_.*\.adoc')


class Tags:
    '''
    defines tags
    '''
    ABSTRACT = '[role="_abstract"]'
    ADD_RES = '[role="_additional-resources"]'
    EXPERIMENTAL = ':experimental:'
    LVLOFFSET = ':leveloffset:'


def print_fail(message, files):
    '''
    fail message that gets called when the check fails
    '''
    print(Colors.FAIL + Colors.BOLD + "FAIL: " + message + ":" + Colors.END, files, sep='\n')


def print_warn(message, files):
    '''
    warning message that gets called when the check result isn't enough to fail
    but sufficient to warn the user
    '''
    print(Colors.WARN + Colors.BOLD + "WARNING: " + message + ":" + Colors.END, files, sep='\n')


def vanilla_xref_check(stripped_file, file):
    '''
    checks if the file contains vanilla xrefs
    '''
    if re.findall(Regex.VANILLA_XREF, stripped_file):
        print_fail("vanilla xrefs found in the following files", file)


def var_in_title_check(stripped_file, file):
    '''
    checks if the file contains a variable in the level 1 heading
    '''
    if re.findall(Regex.VAR_IN_TITLE, stripped_file):
        print_fail("the following files have variable in the level 1 heading", file)


def inline_anchor_check(stripped_file, file):
    '''
    checks if the in-line anchor directly follows the level 1 heading
    '''
    if re.findall(Regex.INLINE_ANCHOR, stripped_file):
        print_fail("in-line anchors found in the following files", file)


def experimental_tag_check(stripped_file, file):
    '''
    checks if the experimental tag is set
    '''
    if stripped_file.count(Tags.EXPERIMENTAL) > 0:
        return
    elif re.findall(Regex.UI_MACROS, stripped_file):
            print_fail("experimental tag is missing in the following files", file)


def html_markup_check(stripped_file, file):
    '''
    checks if HTML markup is present in the file
    '''
    if re.findall(Regex.HTML_MARKUP, stripped_file):
        print_fail("HTML markup is found in the following files", file)


def nesting_in_assemblies_check(stripped_file, file):
    '''
    checks if file contains nested assemblies
    '''
    name_of_file = os.path.basename(file)
    if FileType.ASSEMBLY.fullmatch(name_of_file):
        if re.findall(Regex.NESTED_ASSEMBLY, stripped_file):
            print_fail("the following files contain nested assemblies", file)
        if re.findall(Tags.LVLOFFSET, stripped_file):
            print_fail("the following files contain unsupported includes", file)


def nesting_in_modules_check(stripped_file, file):
    '''
    checks if modules contains nested content
    '''
    name_of_file = os.path.basename(file)
    if not FileType.ASSEMBLY.fullmatch(name_of_file):
        if re.findall(Regex.NESTED_ASSEMBLY, stripped_file):
            print_fail("the following module contains nested assemblies", file)
        if re.findall(Regex.NESTED_MODULES, stripped_file):
            print_fail("the following module contains nested modules", file)


def human_readable_label_check(stripped_file, file):
    '''
    checks if the human readable label is present
    '''
    if re.findall(Regex.HUMAN_READABLE_LABEL_XREF, stripped_file):
        print_fail("the following files have xrefs without a human readable label", file)


def abstarct_section_check(stripped_file, original_file, file):
    '''
    checks if everything related to abstract section is OK
    '''
    occurrences_abstract_tag = stripped_file.count(Tags.ABSTRACT)
    if occurrences_abstract_tag == 0:
        print_fail("abstract tag is missing in the following files", file)
        return
    if occurrences_abstract_tag > 1:
        print_fail("abstract tag appears multiple times in the following files", file)
        return
    # if the abstract tag is only set once:
    if re.findall(Regex.FIRST_PARA, original_file):
        print_fail("there is no line between the level 1 heading and the abstract tag in the following files. the first paragraph might render incorrectly", file)
        return
    if re.findall(Regex.NO_EMPTY_LINE_BEFORE_ABSTRACT, original_file):
        print_fail("the following files have no empty line before the abstract tag", file)
    if re.findall(Regex.EMPTY_LINE_AFTER_ABSTRACT, original_file):
        print_fail("the following files have an empty line after the abstract tag", file)
        return
    if re.findall(Regex.COMMENT_AFTER_ABSTRACT, original_file):
        print_fail("the following files have an comment after the abstract tag", file)


def add_res_section_check(stripped_file, original_file, file):
    '''
    checks if everything related to additional resources section is OK
    '''
    if re.findall(Regex.RELATED_INFO, stripped_file):
        print_fail("'Related information' section was found in the following files. Change the section name to 'Additional resources'", file)
        return
    if not re.findall(Regex.ADDITIONAL_RES, stripped_file):
        return
    # if the file has additional resources section:
    name_of_file = os.path.basename(file)
    if FileType.ASSEMBLY.fullmatch(name_of_file):
        if not re.findall(Regex.ADD_RES_ASSEMBLY, stripped_file):
            print_fail("additional resources section for assemblies should be `== Additional resources`", file)
    elif not re.findall(Regex.ADD_RES_MODULE, stripped_file):
            print_fail("additional resources section for modules should be `.Additional resources`", file)
    if stripped_file.count(Tags.ADD_RES) == 0:
        print_fail("additional resources tag is missing in the found in the following files", file)
        return
    if stripped_file.count(Tags.ADD_RES) > 1:
        print_fail("additional resources tag appears multiple times in the following files", file)
    if stripped_file.count(Tags.ADD_RES) == 1:
        if re.findall(Regex.EMPTY_LINE_AFTER_ADD_RES_TAG, original_file):
            print_fail("the following files have an empty line after the additional resources tag", file)
        elif re.findall(Regex.COMMENT_AFTER_ADD_RES_TAG, original_file):
            print_fail("the following files have comments after the additional resources tag", file)
        if re.findall(Regex.EMPTY_LINE_AFTER_ADD_RES_HEADER, original_file):
            print_fail("the following files have an empty line after the additional resources header", file)
        elif re.findall(Regex.COMMENT_AFTER_ADD_RES_HEADER, original_file):
            print_fail("the following files have comments after the additional resources header", file)


def validation(file_name):
    '''
    opens the file and runs the checks
    '''
    with open(file_name, "r") as file:
        original = file.read()
        stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
        stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
        # FIXME: figure out a better way to exclude pseudo vanilla xrefs
        stripped = Regex.PSEUDO_VANILLA_XREF.sub('', stripped)
        stripped = Regex.CODE_BLOCK.sub('', stripped)

        experimental_tag_check(stripped, file_name)
        var_in_title_check(stripped, file_name)
        inline_anchor_check(stripped, file_name)
        abstarct_section_check(stripped, original, file_name)
        nesting_in_assemblies_check(stripped, file_name)
        nesting_in_modules_check(stripped, file_name)
        vanilla_xref_check(stripped, file_name)
        html_markup_check(stripped, file_name)
        human_readable_label_check(stripped, file_name)
        add_res_section_check(stripped, original, file_name)


validation(FILENAME)
