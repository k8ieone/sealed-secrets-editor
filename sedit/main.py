#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import yaml
import json
import base64
import tempfile
import platform

# representer for strings in literal style
# Thanks to https://stackoverflow.com/questions/20805418/pyyaml-dump-format
class literal_unicode(str): pass
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
yaml.add_representer(literal_unicode, literal_unicode_representer)

def main():
    parser = argparse.ArgumentParser(prog="sedit",
                                description="Easily edit sealed-secrets")
    parser.add_argument("sealed_file", help="Location of the file to edit")
    parser.add_argument("--kubeseal-args", help="Additional arguments to be passed to kubeseal")
    args = parser.parse_args()

    filepath = pathlib.Path(args.sealed_file)
    check_file(filepath)
    file_content = read_file(filepath)

    sealed_secrets = parse_documents(file_content)
    secrets = []

    for document in sealed_secrets:
        namespace = get_doc_metadata(document, "namespace")
        name = get_doc_metadata(document, "name")
        secret = get_secret(name, namespace)
        clean_unneded_fields(secret)
        decode_strings(secret)
        secrets.append(secret)
    tmpname = write_temp(secrets)
    edit_secret(tmpname)
    wait_for_exit()
    seal_output = seal(tmpname, args.kubeseal_args)
    overwrite_sealed(filepath, seal_output)

def check_file(filepath):
    # TODO: Could be more sophisticated
    if not filepath.exists() or filepath.is_dir():
        print("Could not open file: \"{}\"".format(filepath.absolute()))
        exit(1)

def read_file(filepath):
    with open(filepath, 'r') as input_file:
        content = input_file.read()
    return content

def parse_documents(content):
    gen = yaml.safe_load_all(content)
    documents = []
    try:
        for document in list(gen):
            documents.append(dict(document))
    except yaml.scanner.ScannerError as exc:
        print(exc)
        exit(1)
    return documents

def get_doc_metadata(document, field):
    # TODO: Safety, exceptions?
    if field in document["spec"]["template"]["metadata"].keys():
        return document["spec"]["template"]["metadata"][field]

def get_secret(name, namespace):
    data = subprocess.run(["kubectl", "-n", namespace, "get", "secret", name, "-o", "jsonpath='{}'"], capture_output=True, text=True).stdout.strip()
    data = json.loads(data[:-1][1:])
    return data

def clean_unneded_fields(secret):
    metadata_keys = ["creationTimestamp", "managedFields", "uid", "resourceVersion", "ownerReferences"]
    for key in metadata_keys:
        if key in secret["metadata"].keys():
            secret["metadata"].pop(key)

def decode_strings(secret):
    data_to_remove = []
    for key in secret["data"]:
        data = base64.b64decode(secret["data"][key])
        try:
            string_data = data.decode('utf-8')
        except UnicodeDecodeError:
            print("{} is not a string".format(key))
        else:
            if "stringData" not in secret.keys():
                secret["stringData"] = {}
            if "\n" in string_data:
                secret["stringData"][key] = literal_unicode(string_data)
            else:
                secret["stringData"][key] = string_data
            data_to_remove.append(key)
    for key in data_to_remove:
        secret["data"].pop(key)
    if len(secret["data"].keys()) == 0:
        secret.pop("data")

def write_temp(documents):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml') as tmp:
        tmp.write(yaml.dump_all(documents).encode('utf-8'))
        tmpname = tmp.name
    return tmpname

def edit_secret(filepath):
    if platform.system() == 'Darwin':
        subprocess.run(["open", filepath])
    elif platform.system() == 'Windows':
        os.startfile(filepath)
    else:
        subprocess.run(["xdg-open", filepath])

def wait_for_exit():
    # TODO: Find a nicer way to do this
    input("Press Enter after you're finished editing...")

def seal(filepath, kubesealargs):
    # Needs to pass namespace as an argument
    base_command = ["kubeseal", "-o", "yaml"]
    if kubesealargs is not None:
        command = base_command + kubesealargs.split(" ")
    else:
        command = base_command

    with open(filepath, 'r') as file:
        data = file.read()

    output = subprocess.run(command, input=data, capture_output=True, text=True).stdout
    return output

def overwrite_sealed(filepath, content):
    with open(filepath, "w") as f:
        f.write(content)
