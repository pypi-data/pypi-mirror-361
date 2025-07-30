Changelog
=========

0.0.4 (2025-07-11)
------------------

- using new prefixed image segmentation methods like `imgseg_from_bluechannel` instead of `to_bluechannel`


0.0.3 (2025-04-03)
------------------

- added `--resume_from` option to relevant readers that allows resuming the data processing
  from the first file that matches this glob expression (e.g., `*/012345.txt`)
- the `from-paddle-is` reader and `to-paddle-is` writer support custom separators for the text
  files linking image and annotation, e.g., one can use a semi-colon instead of the default
  space when file names should contain spaces as well
  (use `separator: ;` in the `train_dataset` and `val_dataset` sections)
- the `to-paddle-ic` writer now raises an exception if it encounters a space in an image name
- new grouping support added to writers via the `--split_group` option


0.0.2 (2025-03-14)
------------------

- added placeholder support: `from-paddle-ic`, `from-paddle-is`, `to-paddle-ic`, and `to-paddle-is`


0.0.1 (2025-02-11)
------------------

- initial release

