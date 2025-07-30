# uDictionary

A dictionary wrapper.

Avoids exceptions.

## Methods

### Construction

- **uDictionary(*in_dict*={})**: Construct with a python dictionary

### Getters

- **HasValue(*in_name*)**: Returns True if dictionary has a value
- **GetValue(*in_name*)**: Retreive a value
- **GetNumber(*in_name*)**: Convert value to int
- **GetList(*in_name*,*in_separator*=',')**: Convert value to a list

### Setters

- **SetValue(*in_name*, *in_value*)**: Set a value
- **MergeValues(*in_dict*, *in_overwrite*=False)**: Merge values from another dictionary into this one.  If in_overwrite is True, values of the same name will be overwritten

### Copy

- **Copy()**: Make a shallow copy of this object.
- **GetDictionary(*in_copy*=True)**: Return the internal dictionary.  If in_copy is true, this is a shallow copy.
