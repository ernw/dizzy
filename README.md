# dizz file

So, now a short introduction to dizzy packet and protocol specifications:

A single packet is described by a so called dizz file.
Some example files can be found in the dizzes folder that comes with dizzy.
These files are python code so you need to write them in python syntax and format rules.
They consist of 2 variables which need to be defined.

The first var is called `objects` and describes the fields of the packet.
Its a python array of objects with a specific [interface](Interface-of-dizz-object):
```python
objects = [
    ...
    ]
```

The following list show the pre-defined classes which is has implemented the [interface](Interface-of-dizz-object) 
already and are imported in a dizz file:
- `Field()` is the standard class to defined a field.
  The class takes 6 arguments, which are:
  * `name` (**REQUIRED**) have to be a `str()`, which is the name of the field (it to be unique in the packet).
  * `default` (**`=b''`**) have to be a `bytes`, `int` or `str()`, which is the default value of the field.
  * `size` (**`=None`**) have to be a `int()` or `slice()` (in bits).  
    If it is `None` than the field has the same size as the default value.
    With `slice()` a variable size can be defined.
  * `fuzz` (**`="none"`**) have to be a `str()`, which is defined the fuzzing mode for the field.  
    The fuzzing mode for that field can be `"none"` for not fuzzing that field at all, `"std"` for fuzzing some values 
    on the upper and lower value border, and `"full"` for fuzzing all possible values.
  * `endian` (**="!"**) have to be a `str()`, which is defined the endianness of the field when the default value is a 
    `int()`  
    The endianss for that argument can be `"!"` for network (=big-endian), `"<"` for little-endian or `">"` for 
    big-endian.
  * `encoding` (**`=CONFIG["GLOBALS"]["CODEC"]`**) have to be a `str`, which defined the encoding schema of the default 
    value if it is a `str()`  
  
  Example:
  ```python
  ...
  objects = [
      Field("length_field", b"\x00" * 8), # 8 byte length filed
      Field("variable_sized_field", b"\x00" * 8, slice(2, 20, 2))
      ...
      ]
  ...
  ```
- `List()` is a field, which have a list of value from a file.
  The class takes 4 arguments, which are:
  * `name` (**REQUIRED**) have to be a `str()`, which is the name of the field (it to be unique in the packet).
  * `path` (**`=CONFIG["GLOBALS"]["DEFAULT_STR_LIB"]`**) have to be a `str()`, which defined the path to the file (one value per line, all values will be inserted 
     while fuzzing)
  * `encoding` (**`=CONFIG["GLOBALS"]["CODEC"]`**) have to be a `str`, which defined the encoding list.
  * `default` (**`=None`**) have to be `bytes()`, which defined the first value of the list. 
  
  Example:   
    ```python
    ...
    objects = [
        Field("length_field", b"\x00" * 8), # 8 byte length filed
        List("list_of_values", "/lists/test.txt", default=b"First value"), # new line separated list
    ...
    ]
   ```

The second var is called `functions` and is for execute some code to change the value of the fields.
Its a python array of functions with a specific [interface](Interface-of-dizz-function):
```python
functions = [
    ...
    ]
```

The following list show the pre-defined functions which is has the [interface](Interface-of-dizz-object) already and are
 imported in a dizz file:
- `link` is a function to copy the value of a field into another field per mutation.
  So that target field has the same value as the source field during the fuzzing.
  The function takes 2 arguments, which are:
  * `source` (**REQUIRED**) have to be a `str()`, which defined the name of the source field.
  * `target` (**REQUIRED**) have to be a `str()`, which defined the name of the target field.
  
  Example:
  ```python
  ...
  objects = [
      Field("source_field", b"\xaa", fuzz="full"),
      Field("target_field", b"\x00", fuzz="none"), # this field has always the same value as source_field
      ...
    ]
  
  functions = [
      link("source_field", "target_field"),
      ...
  ]
  ```
- `length` is a function to save the current size(in bits) of fields in a dedicated length field.
  This function is useful for example when the packet has a Type Length Value structure.
  The function takes 3s arguments, which are:
  * `target` (**REQUIRED**) have to be a `str()`, which defined the name of the field to save the length.
  * `start` (**`=START`**) have to be a `str()`, which defined where the function should start to count the length.
    The default parameter of this argument(`=START`) means to start at the beginning of the packet.
  * `stop` (**`=STOP`**) have to be a `str()`, which defined where the function should stop(inclusive) to count the 
    length.
    The default parameter of this argument(`=STOP`) means to start at the end of the packet.
  
  Example:
  ```python
  objects = [
      Field("field0", b"\xaa" * 2, fuzz="full"),
      Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
      # calculate the current size of the field0 und field1 in bits and saves the size in length_field
      Field("length_field", b"\x00\x00", endian="<", fuzz="none"), 
      ...
    ]

  functions = [
      length("length_field", "field0", "field1"),
      ...
  ]
  ```
- `length_bytes` is a function same as `length` but the length is saved in bytes.
  The function takes 3 arguments, which are:
  * `target` (**REQUIRED**) have to be a `str()`, which defined the name of the field to save the length.
  * `start` (**`=START`**) have to be a `str()`, which defined where the function should start to count the length.
    The default parameter of this argument(`=START`) means to start at the beginning of the packet.
  * `stop` (**`=STOP`**) have to be a `str()`, which defined where the function should stop(inclusive) to count the 
    length.
    The default parameter of this argument(`=STOP`) means to start at the end of the packet.
    
  Example:
  ```python
  objects = [
      Field("field0", b"\xaa" * 2, fuzz="full"),
      Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
      # calculate the current size of the field0 und field1 in bytes and saves the size in length_field
      Field("length_field", b"\x00\x00", endian="<", fuzz="none"), 
      ...
    ]

  functions = [
      length_bytes("length_field", "field0", "field1"),
      ...
  ]
  ```
    
- `length_string_bytes` is a function same as `length_bytes` but the length is saved in bytes and as `str()`.
  The function takes 4 arguments, which are:
  * `target` (**REQUIRED**) have to be a `str()`, which defined the name of the field to save the length.
  * `start` (**`=START`**) have to be a `str()`, which defined where the function should start to count the length.
    The default parameter of this argument(`=START`) means to start at the beginning of the packet.
  * `stop` (**`=STOP`**) have to be a `str()`, which defined where the function should stop(inclusive) to count the 
    length.
    The default parameter of this argument(`=STOP`) means to start at the end of the packet.
  * `encoding` (**`=CONFIG["GLOBALS"]["CODEC"]`**) have to be a `str`, which defined the encoding of string.
  
  Example:
  ```python
  objects = [
      Field("field0", b"\xaa" * 2, fuzz="full"),
      Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
      # calculate the current size of the field0 und field1 in bytes as and saves the size as string in length_field
      Field("length_field", b"\x00\x00", endian="<", fuzz="none"), 
      ...
    ]

  functions = [
      length_string_bytes("length_field", "field0", "field1"),
      ...
  ]
  ```
- `length_lambda` is a function same as `length` but the length is pass to a function and the return value of the function
  is saved in a dedicated length field.
  The function takes 4 arguments, which are:
  * `lam` (**REQUIRED**) have to be a function(mostly a lambda function), to pass the size(so the function has 1 
     argument).
  * `target` (**REQUIRED**) have to be a `str()`, which defined the name of the field to save the length.
  * `start` (**`=START`**) have to be a `str()`, which defined where the function should start to count the length.
    The default parameter of this argument(`=START`) means to start at the beginning of the packet.
  * `stop` (**`=STOP`**) have to be a `str()`, which defined where the function should stop(inclusive) to count the 
    length.
    The default parameter of this argument(`=STOP`) means to start at the end of the packet.
  * `encoding` (**`=CONFIG["GLOBALS"]["CODEC"]`**) have to be a `str`, which defined the encoding of string.
  
  Example:
  ```python
  objects = [
      Field("field0", b"\xaa" * 2, fuzz="full"),
      Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
      # calculate the current size of the field0 und field1 in bits and pass it to the lambda function and saves the 
      # return value into the length_field
      Field("length_field", b"\x00\x00", endian="<", fuzz="none"), 
      ...
    ]

  functions = [
      length_lambda(lambda x: x + 1, "length_field", "field0", "field1"),
      ...
  ]
  ```
- `chechsum` is a function that calculate a checksum over fields and save the value to a dedicate field.
  The function takes 4 arguments, which are:
  * `target` (**REQUIRED**) have to be a `str()`, which defined where to save the checksum.
  * `start` (**REQUIRED**) have to be a `str()`, which defined where the function should start to calculate the 
    checksum.
  * `stop` (**REQUIRED**) have to be a `str()`, which defined where the function should stop(inclusive) to calculate the 
    checksum.
  * `algorithm` (**REQUIRED**) have to be a `str()`, which defined the algorithm to use for the checksum.
    The possible value for this argument are:
      - `"md5"` for Message-Digest Algorithm 5
      - `"sha1"` for Secure Hash Algorithm 1
      - `"sha224"` for Secure Hash Algorithm 2 with a hash length of 224 bits
      - `"sha256"` for Secure Hash Algorithm 2 with a hash length of 256 bits
      - `"sha384"` for Secure Hash Algorithm 2 with a hash length of 384 bits
      - `"sha512"` for Secure Hash Algorithm 2 with a hash length of 512 bits
    
    Example:
    ```python
    objects = [
        Field("field0", b"\xaa" * 2, fuzz="full"),
        Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
        # calculate the checksum of field0 and field1 and save it to checksum_field (the size of checksum_field is the
        # same, if the checksum value is bigger than the size of the field then it would be truncate)
        Field("checksum_field", b"\x00\x00\x00\x00"), 
        ...
    ]
    functions = [
        chechsum("checksum_field", "field0", "field1", "md5"),
        ...
    ]
    ```
- `checksum_inet` is a function that calculate a checksum over field by using the algorithm 'inet' (rfc1071) and save 
  the to a dedicate field.
  The function take 3 arhuments, which are:
  * `target` (**REQUIRED**) have to be a `str()`, which defined where to save the checksum.
  * `start` (**REQUIRED**) have to be a `str()`, which defined where the function should start to calculate the 
    checksum.
  * `stop` (**REQUIRED**) have to be a `str()`, which defined where the function should stop(inclusive) to calculate the 
    checksum.
    
    Example:
    ```python
    objects = [
        Field("field0", b"\xaa" * 2, fuzz="full"),
        Field("field1", b"\xaa" * 2, slice(4, 9), fuzz="full"),
        # calculate the checksum of field0 and field1 and save it to checksum_field
        Field("checksum_field", b"\x00\x00\x00\x00"), 
        ...
    ]
    functions = [
        checksum_inet("checksum_field", "field0", "field1", "md5"),
        ...
    ]
    ```

# act file

Ok, that are the packet descriptions so far.
Ones you want to get state full, you need to write interaction in act files. 
Some prepared can be found in the interactions folder that comes with dizzy. 
These file are python code as well.
They consist of 2 variables which need to be defined.

The first var is called `objects` which is a python list of `Dizz()`.   
`Dict()` is a class, which have 6 arguments:
- `name` (**REQUIRED**) have to be a `str()`, which is the name of the packet (it to be unique in the interaction).
- `filename` (**REQUIRED**) have to be a `str()`, which is the path of the dizz file.
- `readback` (**`=0`**) have to be a `int()`, which defined how many bytes at least to read after the packet was send.
- `fuzz` (**`="std"`**) have to be a `str()`, which define the fuzzing mode for this packet.
   The fuzzing mode for that packet can be `"none"` for not fuzzing that packet at all, `"std"` for fuzzing each field 
   at once, and `"full"` for fuzzing all fields by using the cross product.
- `start_at` (**`=0`**) have to be a `int()`, which defined at which iteration the packet should start.
- `config_values` (**`={}`**) have to be a `dict()`, which defined the configuration values for the packet.

```python
objects = [
    # define the first packet of the interaction and after the packet is send it have read at least 100 bytes from the 
    # session 
    Dizz("first_packet", "module_name/dizzes/first_packet.dizz", 100, fuzz="full"),
    Dizz("second_packet", "module_name/dizzes/second_packet.dizz"),
    ...
    ]
```
 
The second var is called `functions`, which is this case a python `dict()`.
For more information about act `functions` see [Interface](interface-of-act-function).
The following example takes the value of the `field0` dizz object of the dizz packet `Dizz0` and assigned it to the 
`field0` of the dizz packet `Dizz3`:
```python
def test(interaction_iterator, dizzy_iterator, response):
    buf0 = response[0:10]
    dizzy_iterator["field4"] = buf0
    buf1 = interaction_iterator["Dizz0"]["field0"]
    interaction_iterator["Dizz3"]["field0"] = buf1


