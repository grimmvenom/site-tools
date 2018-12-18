# file-sorting

## Summary
This tool can recursively rename directories and files that contain spaces, then has the ability to replace all references in files to the old path, with the new path.


## Options

### Define directory
-d "PathToDirectory"

### Define File Extensions
--ext ".FileExtensionHere"

### Rename Directories
--rename-dirs

### Replace References
--replace-references

## Example Command
python ./rename-replace-references.py -d "~/Documents" --ext ".txt" --rename-dirs --replace-References

