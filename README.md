# sealed-secrets-editor

**Problem:** "Editing sealed-secrets is difficult. I need to go to the cluster, get the current version of the secret, base64-decode it, paste it into my editor, make changes and seal it again."

**Solution:** Use `sedit`! This ~150 LoC script does exactly the above mentioned flow automatically.

1. Parse the YAML file for all documents
2. Get the namespace and name from the sealed-secret
3. Get the contents of the secret from the cluster using kubectl
4. Remove unneeded fields
5. base64 decode stuff in data and move it to stringData
6. Skip decoding binary data - keep in data
7. Open the secret in the system default editor
8. Wait for exit
9. Seal the secret and overwrite the sealed-secret

## Usage

`sedit sealed-secret.yaml`

Save your edited file afterwards and press enter to seal the new secret.

See the `-h` option for help.

## Limitations

Currently the tool requires the sealed-secret to be in YAML format instad of JSON.  
This choice was made, so that multiple sealed-secrets (YAML documents) can be stored in a single file. JSON doesn't support this.
