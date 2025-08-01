.. _playbooks_filters:

********************************
Using filters to manipulate data
********************************

Filters let you transform JSON data into YAML data, split a URL to extract the hostname, get the SHA1 hash of a string, add or multiply integers, and much more. You can use the Ansible-specific filters documented here to manipulate your data, or use any of the standard filters shipped with Jinja2 - see the list of :ref:`built-in filters <jinja2:builtin-filters>` in the official Jinja2 template documentation. You can also use :ref:`Python methods <jinja2:python-methods>` to transform data. You can :ref:`create custom Ansible filters as plugins <developing_filter_plugins>`, though we generally welcome new filters into the ansible-core repo so everyone can use them.

Because templating happens on the Ansible control node, **not** on the target host, filters execute on the control node and transform data locally.

.. contents::
   :local:

Handling undefined variables
============================

Filters can help you manage missing or undefined variables by providing defaults or making some variables optional. If you configure Ansible to ignore most undefined variables, you can mark some variables as requiring values with the ``mandatory`` filter.

.. _defaulting_undefined_variables:

Providing default values
------------------------

You can provide default values for variables directly in your templates using the Jinja2 'default' filter. This is often a better approach than failing if a variable is not defined:

.. code-block:: jinja

    {{ some_variable | default(5) }}

In the above example, if the variable 'some_variable' is not defined, Ansible uses the default value 5, rather than raising an "undefined variable" error and failing. If you are working within a role, you can also add role defaults to define the default values for variables in your role. To learn more about role defaults see :ref:`Role directory structure <role_directory_structure>`.

Beginning in version 2.8, attempting to access an attribute of an Undefined value in Jinja will return another Undefined value, rather than throwing an error immediately. This means that you can now simply use
a default with a value in a nested data structure (in other words, :code:`{{ foo.bar.baz | default('DEFAULT') }}`) when you do not know if the intermediate values are defined.

If you want to use the default value when variables evaluate to false or an empty string you have to set the second parameter to ``true``:

.. code-block:: jinja

    {{ lookup('env', 'MY_USER') | default('admin', true) }}

.. _omitting_undefined_variables:

Making variables optional
-------------------------

By default, Ansible requires values for all variables in a templated expression. However, you can make specific module variables optional. For example, you might want to use a system default for some items and control the value for others. To make a module variable optional, set the default value to the special variable ``omit``:

.. code-block:: yaml+jinja

    - name: Touch files with an optional mode
      ansible.builtin.file:
        dest: "{{ item.path }}"
        state: touch
        mode: "{{ item.mode | default(omit) }}"
      loop:
        - path: /tmp/foo
        - path: /tmp/bar
        - path: /tmp/baz
          mode: "0444"

In this example, the default mode for the files ``/tmp/foo`` and ``/tmp/bar`` is determined by the umask of the system. Ansible does not send a value for ``mode``. Only the third file, ``/tmp/baz``, receives the `mode=0444` option.

.. note:: If you are "chaining" additional filters after the ``default(omit)`` filter, you should instead do something like this:
      ``"{{ foo | default(None) | some_filter or omit }}"``. In this example, the default ``None`` (Python null) value will cause the later filters to fail, which will trigger the ``or omit`` portion of the logic. Using ``omit`` in this manner is very specific to the later filters you are chaining though, so be prepared for some trial and error if you do this.

.. _forcing_variables_to_be_defined:

Defining mandatory values
-------------------------

If you configure Ansible to ignore undefined variables, you may want to define some values as mandatory. By default, Ansible fails if a variable in your playbook or command is undefined. You can configure Ansible to allow undefined variables by setting :ref:`DEFAULT_UNDEFINED_VAR_BEHAVIOR` to ``false``. In that case, you may want to require some variables to be defined. You can do this with:

.. code-block:: jinja

    {{ variable | mandatory }}

The variable value will be used as is, but the template evaluation will raise an error if it is undefined.

A convenient way of requiring a variable to be overridden is to give it an undefined value using the :ref:`undef() <templating_undef>` function.

.. code-block:: yaml+jinja

    galaxy_url: "https://galaxy.ansible.com"
    galaxy_api_key: "{{ undef(hint='You must specify your Galaxy API key') }}"

Defining different values for true/false/null (ternary)
=======================================================

You can create a test, then define one value to use when the test returns true and another when the test returns false (new in version 1.9):

.. code-block:: jinja

    {{ (status == 'needs_restart') | ternary('restart', 'continue') }}

In addition, you can define one value to use on true, one value on false and a third value on null (new in version 2.8):

.. code-block:: jinja

   {{ enabled | ternary('no shutdown', 'shutdown', omit) }}

Managing data types
===================

You might need to know, change, or set the data type on a variable. For example, a registered variable might contain a dictionary when your next task needs a list, or a user :ref:`prompt <playbooks_prompts>` might return a string when your playbook needs a boolean value. Use the :ansplugin:`ansible.builtin.type_debug#filter`, :ansplugin:`ansible.builtin.dict2items#filter`, and :ansplugin:`ansible.builtin.items2dict#filter` filters to manage data types. You can also use the data type itself to cast a value as a specific data type.

Discovering the data type
-------------------------

.. versionadded:: 2.3

If you are unsure of the underlying Python type of a variable, you can use the :ansplugin:`ansible.builtin.type_debug#filter` filter to display it. This is useful in debugging when you need a particular type of variable:

.. code-block:: jinja

    {{ myvar | type_debug }}

You should note that, while this may seem like a useful filter for checking that you have the right type of data in a variable, you should often prefer :ref:`type tests <type_tests>`, which will allow you to test for specific data types.

Transforming strings into lists
-------------------------------

Use the :ansplugin:`ansible.builtin.split#filter` filter to transform a character/string delimited string into a list of items suitable for :ref:`looping <playbooks_loops>`. For example, if you want to split a string variable `fruits` by commas, you can use:

.. code-block:: jinja

    {{ fruits | split(',') }}

String data (before applying the :ansplugin:`ansible.builtin.split#filter` filter):

.. code-block:: yaml

    fruits: apple,banana,orange

List data (after applying the :ansplugin:`ansible.builtin.split#filter` filter):

.. code-block:: yaml

    - apple
    - banana
    - orange

.. _dict_filter:

Transforming dictionaries into lists
------------------------------------

.. versionadded:: 2.6


Use the :ansplugin:`ansible.builtin.dict2items#filter` filter to transform a dictionary into a list of items suitable for :ref:`looping <playbooks_loops>`:

.. code-block:: yaml+jinja

    {{ dict | dict2items }}

Dictionary data (before applying the :ansplugin:`ansible.builtin.dict2items#filter` filter):

.. code-block:: yaml

    tags:
      Application: payment
      Environment: dev

List data (after applying the :ansplugin:`ansible.builtin.dict2items#filter` filter):

.. code-block:: yaml

    - key: Application
      value: payment
    - key: Environment
      value: dev

.. versionadded:: 2.8

The :ansplugin:`ansible.builtin.dict2items#filter` filter is the reverse of the :ansplugin:`ansible.builtin.items2dict#filter` filter.

If you want to configure the names of the keys, the :ansplugin:`ansible.builtin.dict2items#filter` filter accepts 2 keyword arguments. Pass the :ansopt:`ansible.builtin.dict2items#filter:key_name` and :ansopt:`ansible.builtin.dict2items#filter:value_name` arguments to configure the names of the keys in the list output:

.. code-block:: yaml+jinja

    {{ files | dict2items(key_name='file', value_name='path') }}

Dictionary data (before applying the :ansplugin:`ansible.builtin.dict2items#filter` filter):

.. code-block:: yaml

    files:
      users: /etc/passwd
      groups: /etc/group

List data (after applying the :ansplugin:`ansible.builtin.dict2items#filter` filter):

.. code-block:: yaml

    - file: users
      path: /etc/passwd
    - file: groups
      path: /etc/group


Transforming lists into dictionaries
------------------------------------

.. versionadded:: 2.7

Use the :ansplugin:`ansible.builtin.items2dict#filter` filter to transform a list into a dictionary, mapping the content into ``key: value`` pairs:

.. code-block:: jinja

    {{ tags | items2dict }}

List data (before applying the :ansplugin:`ansible.builtin.items2dict#filter` filter):

.. code-block:: yaml

    tags:
      - key: Application
        value: payment
      - key: Environment
        value: dev

Dictionary data (after applying the :ansplugin:`ansible.builtin.items2dict#filter` filter):

.. code-block:: text

    Application: payment
    Environment: dev

The :ansplugin:`ansible.builtin.items2dict#filter` filter is the reverse of the :ansplugin:`ansible.builtin.dict2items#filter` filter.

Not all lists use ``key`` to designate keys and ``value`` to designate values. For example:

.. code-block:: yaml

    fruits:
      - fruit: apple
        color: red
      - fruit: pear
        color: yellow
      - fruit: grapefruit
        color: yellow

In this example, you must pass the :ansopt:`ansible.builtin.items2dict#filter:key_name` and :ansopt:`ansible.builtin.items2dict#filter:value_name` arguments to configure the transformation. For example:

.. code-block:: jinja

    {{ fruits | items2dict(key_name='fruit', value_name='color') }}

If you do not pass these arguments, or do not pass the correct values for your list, you will see ``KeyError: key`` or ``KeyError: my_typo``.

Forcing the data type
---------------------

You can cast values as certain types. For example, if you expect the input "True" from a :ref:`vars_prompt <playbooks_prompts>` and you want Ansible to recognize it as a boolean value instead of a string:

.. code-block:: yaml

   - ansible.builtin.debug:
        msg: test
     when: some_string_value | bool

If you want to perform a mathematical comparison on a fact and you want Ansible to recognize it as an integer instead of a string:

.. code-block:: yaml

   - shell: echo "only on Red Hat 6, derivatives, and later"
     when: ansible_facts['os_family'] == "RedHat" and ansible_facts['lsb']['major_release'] | int >= 6


.. versionadded:: 1.6

.. _filters_for_formatting_data:

Formatting data: YAML and JSON
==============================

You can switch a data structure in a template from or to JSON or YAML format, with options for formatting, indenting, and loading data. The basic filters are occasionally useful for debugging:

.. code-block:: jinja

    {{ some_variable | to_json }}
    {{ some_variable | to_yaml }}

See :ansplugin:`ansible.builtin.to_json#filter` and :ansplugin:`ansible.builtin.to_yaml#filter` for documentation on these filters.

For human readable output, you can use:

.. code-block:: jinja

    {{ some_variable | to_nice_json }}
    {{ some_variable | to_nice_yaml }}

See :ansplugin:`ansible.builtin.to_nice_json#filter` and :ansplugin:`ansible.builtin.to_nice_yaml#filter` for documentation on these filters.

You can change the indentation of either format:

.. code-block:: jinja

    {{ some_variable | to_nice_json(indent=2) }}
    {{ some_variable | to_nice_yaml(indent=8) }}

The :ansplugin:`ansible.builtin.to_yaml#filter` and :ansplugin:`ansible.builtin.to_nice_yaml#filter` filters use the `PyYAML library`_ which has a default 80 symbol string length limit. That causes an unexpected line break after 80th symbol (if there is a space after 80th symbol)
To avoid such behavior and generate long lines, use the :ansopt:`width` option. You must use a hardcoded number to define the width, instead of a construction like ``float("inf")``, because the filter does not support proxying Python functions. For example:

.. code-block:: jinja

    {{ some_variable | to_yaml(indent=8, width=1337) }}
    {{ some_variable | to_nice_yaml(indent=8, width=1337) }}

The filter does support passing through other YAML parameters. For a full list, see the `PyYAML documentation`_ for ``dump()``.

If you are reading in some already formatted data:

.. code-block:: jinja

    {{ some_variable | from_json }}
    {{ some_variable | from_yaml }}

for example:

.. code-block:: yaml+jinja

  tasks:
    - name: Register JSON output as a variable
      ansible.builtin.shell: cat /some/path/to/file.json
      register: result

    - name: Set a variable
      ansible.builtin.set_fact:
        myvar: "{{ result.stdout | from_json }}"


Filter `to_json` and Unicode support
------------------------------------

By default :ansplugin:`ansible.builtin.to_json#filter` and :ansplugin:`ansible.builtin.to_nice_json#filter` will convert data received to ASCII, so:

.. code-block:: jinja

    {{ 'München'| to_json }}

will return:

.. code-block:: text

    'M\u00fcnchen'

To keep Unicode characters, pass the parameter :ansopt:`ansible.builtin.to_json#filter:ensure_ascii=False` to the filter:

.. code-block:: jinja

    {{ 'München'| to_json(ensure_ascii=False) }}

    'München'

.. versionadded:: 2.7

To parse multi-document YAML strings, the :ansplugin:`ansible.builtin.from_yaml_all#filter` filter is provided.
The :ansplugin:`ansible.builtin.from_yaml_all#filter` filter will return a generator of parsed YAML documents.

for example:

.. code-block:: yaml+jinja

  tasks:
    - name: Register a file content as a variable
      ansible.builtin.shell: cat /some/path/to/multidoc-file.yaml
      register: result

    - name: Print the transformed variable
      ansible.builtin.debug:
        msg: '{{ item }}'
      loop: '{{ result.stdout | from_yaml_all | list }}'

Combining and selecting data
============================

You can combine data from multiple sources and types, and select values from large data structures, giving you precise control over complex data.

.. _zip_filter_example:

Combining items from multiple lists: zip and zip_longest
--------------------------------------------------------

.. versionadded:: 2.3

To get a list combining the elements of other lists use :ansplugin:`ansible.builtin.zip#filter`:

.. code-block:: yaml+jinja

    - name: Give me list combo of two lists
      ansible.builtin.debug:
        msg: "{{ [1,2,3,4,5,6] | zip(['a','b','c','d','e','f']) | list }}"

    # => [[1, "a"], [2, "b"], [3, "c"], [4, "d"], [5, "e"], [6, "f"]]

    - name: Give me the shortest combo of two lists
      ansible.builtin.debug:
        msg: "{{ [1,2,3] | zip(['a','b','c','d','e','f']) | list }}"

    # => [[1, "a"], [2, "b"], [3, "c"]]

To always exhaust all lists use :ansplugin:`ansible.builtin.zip_longest#filter`:

.. code-block:: yaml+jinja

    - name: Give me the longest combo of three lists, fill with X
      ansible.builtin.debug:
        msg: "{{ [1,2,3] | zip_longest(['a','b','c','d','e','f'], [21, 22, 23], fillvalue='X') | list }}"

    # => [[1, "a", 21], [2, "b", 22], [3, "c", 23], ["X", "d", "X"], ["X", "e", "X"], ["X", "f", "X"]]

Similarly to the output of the :ansplugin:`ansible.builtin.items2dict#filter` filter mentioned above, these filters can be used to construct a ``dict``:

.. code-block:: jinja

    {{ dict(keys_list | zip(values_list)) }}

List data (before applying the :ansplugin:`ansible.builtin.zip#filter` filter):

.. code-block:: yaml

    keys_list:
      - one
      - two
    values_list:
      - apple
      - orange

Dictionary data (after applying the :ansplugin:`ansible.builtin.zip#filter` filter):

.. code-block:: yaml

    one: apple
    two: orange

Combining objects and subelements
---------------------------------

.. versionadded:: 2.7

The :ansplugin:`ansible.builtin.subelements#filter` filter produces a product of an object and the subelement values of that object, similar to the :ansplugin:`ansible.builtin.subelements#lookup` lookup. This lets you specify individual subelements to use in a template. For example, this expression:

.. code-block:: jinja

    {{ users | subelements('groups', skip_missing=True) }}

Data before applying the :ansplugin:`ansible.builtin.subelements#filter` filter:

.. code-block:: yaml

    users:
    - name: alice
      authorized:
      - /tmp/alice/onekey.pub
      - /tmp/alice/twokey.pub
      groups:
      - wheel
      - docker
    - name: bob
      authorized:
      - /tmp/bob/id_rsa.pub
      groups:
      - docker

Data after applying the :ansplugin:`ansible.builtin.subelements#filter` filter:

.. code-block:: yaml

    -
      - name: alice
        groups:
        - wheel
        - docker
        authorized:
        - /tmp/alice/onekey.pub
        - /tmp/alice/twokey.pub
      - wheel
    -
      - name: alice
        groups:
        - wheel
        - docker
        authorized:
        - /tmp/alice/onekey.pub
        - /tmp/alice/twokey.pub
      - docker
    -
      - name: bob
        authorized:
        - /tmp/bob/id_rsa.pub
        groups:
        - docker
      - docker

You can use the transformed data with ``loop`` to iterate over the same subelement for multiple objects:

.. code-block:: yaml+jinja

    - name: Set authorized ssh key, extracting just that data from 'users'
      ansible.posix.authorized_key:
        user: "{{ item.0.name }}"
        key: "{{ lookup('file', item.1) }}"
      loop: "{{ users | subelements('authorized') }}"

.. _combine_filter:

Combining hashes/dictionaries
-----------------------------

.. versionadded:: 2.0

The :ansplugin:`ansible.builtin.combine#filter` filter allows hashes to be merged. For example, the following would override keys in one hash:

.. code-block:: jinja

    {{ {'a':1, 'b':2} | combine({'b':3}) }}

The resulting hash would be:

.. code-block:: text

    {'a':1, 'b':3}

The filter can also take multiple arguments to merge:

.. code-block:: jinja

    {{ a | combine(b, c, d) }}
    {{ [a, b, c, d] | combine }}

In this case, keys in ``d`` would override those in ``c``, which would override those in ``b``, and so on.

The filter also accepts two optional parameters: :ansopt:`ansible.builtin.combine#filter:recursive` and :ansopt:`ansible.builtin.combine#filter:list_merge`.

recursive
  Is a boolean, default to ``False``.
  Should the :ansplugin:`ansible.builtin.combine#filter` recursively merge nested hashes.
  Note: It does **not** depend on the value of the ``hash_behaviour`` setting in ``ansible.cfg``.

list_merge
  Is a string, its possible values are ``replace`` (default), ``keep``, ``append``, ``prepend``, ``append_rp`` or ``prepend_rp``.
  It modifies the behavior of :ansplugin:`ansible.builtin.combine#filter` when the hashes to merge contain arrays/lists.

.. code-block:: yaml

    default:
      a:
        x: default
        y: default
      b: default
      c: default
    patch:
      a:
        y: patch
        z: patch
      b: patch

If :ansopt:`ansible.builtin.combine#filter:recursive=False` (the default), nested hash aren't merged:

.. code-block:: yaml+jinja

    {{ default | combine(patch) }}

This would result in:

.. code-block:: yaml

    a:
      y: patch
      z: patch
    b: patch
    c: default

If :ansopt:`ansible.builtin.combine#filter:recursive=True`, recurse into a nested hash and merge their keys:

.. code-block:: yaml+jinja

    {{ default | combine(patch, recursive=True) }}

This would result in:

.. code-block:: yaml

    a:
      x: default
      y: patch
      z: patch
    b: patch
    c: default

If :ansopt:`ansible.builtin.combine#filter:list_merge='replace'` (the default), arrays from the right hash will "replace" the ones in the left hash:

.. code-block:: yaml

    default:
      a:
        - default
    patch:
      a:
        - patch

.. code-block:: yaml+jinja

    {{ default | combine(patch) }}

This would result in:

.. code-block:: yaml

    a:
      - patch

If :ansopt:`ansible.builtin.combine#filter:list_merge='keep'`, arrays from the left hash will be kept:

.. code-block:: yaml+jinja

    {{ default | combine(patch, list_merge='keep') }}

This would result in:

.. code-block:: yaml

    a:
      - default

If :ansopt:`ansible.builtin.combine#filter:list_merge='append'`, arrays from the right hash will be appended to the ones in the left hash:

.. code-block:: yaml+jinja

    {{ default | combine(patch, list_merge='append') }}

This would result in:

.. code-block:: yaml

    a:
      - default
      - patch

If :ansopt:`ansible.builtin.combine#filter:list_merge='prepend'`, arrays from the right hash will be prepended to the ones in the left hash:

.. code-block:: yaml+jinja

    {{ default | combine(patch, list_merge='prepend') }}

This would result in:

.. code-block:: yaml

    a:
      - patch
      - default

If :ansopt:`ansible.builtin.combine#filter:list_merge='append_rp'`, arrays from the right hash will be appended to the ones in the left hash. Elements of arrays in the left hash that are also in the corresponding array of the right hash will be removed ("rp" stands for "remove present"). Duplicate elements that aren't in both hashes are kept:

.. code-block:: yaml

    default:
      a:
        - 1
        - 1
        - 2
        - 3
    patch:
      a:
        - 3
        - 4
        - 5
        - 5

.. code-block:: yaml+jinja

    {{ default | combine(patch, list_merge='append_rp') }}

This would result in:

.. code-block:: yaml

    a:
      - 1
      - 1
      - 2
      - 3
      - 4
      - 5
      - 5

If :ansopt:`ansible.builtin.combine#filter:list_merge='prepend_rp'`, the behavior is similar to the one for ``append_rp``, but elements of arrays in the right hash are prepended:

.. code-block:: yaml+jinja

    {{ default | combine(patch, list_merge='prepend_rp') }}

This would result in:

.. code-block:: yaml

    a:
      - 3
      - 4
      - 5
      - 5
      - 1
      - 1
      - 2

:ansopt:`ansible.builtin.combine#filter:recursive` and :ansopt:`ansible.builtin.combine#filter:list_merge` can be used together:

.. code-block:: yaml

    default:
      a:
        a':
          x: default_value
          y: default_value
          list:
            - default_value
      b:
        - 1
        - 1
        - 2
        - 3
    patch:
      a:
        a':
          y: patch_value
          z: patch_value
          list:
            - patch_value
      b:
        - 3
        - 4
        - 4
        - key: value

.. code-block:: yaml+jinja

    {{ default | combine(patch, recursive=True, list_merge='append_rp') }}

This would result in:

.. code-block:: yaml

    a:
      a':
        x: default_value
        y: patch_value
        z: patch_value
        list:
          - default_value
          - patch_value
    b:
      - 1
      - 1
      - 2
      - 3
      - 4
      - 4
      - key: value


.. _extract_filter:

Selecting values from arrays or hashtables
-------------------------------------------

.. versionadded:: 2.1

The `extract` filter is used to map from a list of indices to a list of values from a container (hash or array):

.. code-block:: jinja

    {{ [0,2] | map('extract', ['x','y','z']) | list }}
    {{ ['x','y'] | map('extract', {'x': 42, 'y': 31}) | list }}

The results of the above expressions would be:

.. code-block:: none

    ['x', 'z']
    [42, 31]

The filter can take another argument:

.. code-block:: jinja

    {{ groups['x'] | map('extract', hostvars, 'ec2_ip_address') | list }}

This takes the list of hosts in group 'x', looks them up in `hostvars`, and then looks up the `ec2_ip_address` of the result. The final result is a list of IP addresses for the hosts in group 'x'.

The third argument to the filter can also be a list, for a recursive lookup inside the container:

.. code-block:: jinja

    {{ ['a'] | map('extract', b, ['x','y']) | list }}

This would return a list containing the value of `b['a']['x']['y']`.

Combining lists
---------------

This set of filters returns a list of combined lists.


permutations
^^^^^^^^^^^^
To get permutations of a list:

.. code-block:: yaml+jinja

    - name: Give me the largest permutations (order matters)
      ansible.builtin.debug:
        msg: "{{ [1,2,3,4,5] | ansible.builtin.permutations | list }}"
    # => [(1, 2, 3, 4, 5), (1, 2, 3, 5, 4), (1, 2, 4, 3, 5), (1, 2, 4, 5, 3), (1, 2, 5, 3, 4), (1, 2, 5, 4, 3), (1, 3, 2, 4, 5), (1, 3, 2, 5, 4), (1, 3, 4, 2, 5), (1, 3, 4, 5, 2), (1, 3, 5, 2, 4), (1, 3, 5, 4, 2), (1, 4, 2, 3, 5), (1, 4, 2, 5, 3), (1, 4, 3, 2, 5), (1, 4, 3, 5, 2), (1, 4, 5, 2, 3), (1, 4, 5, 3, 2), (1, 5, 2, 3, 4), (1, 5, 2, 4, 3), (1, 5, 3, 2, 4), (1, 5, 3, 4, 2), (1, 5, 4, 2, 3), (1, 5, 4, 3, 2), (2, 1, 3, 4, 5), (2, 1, 3, 5, 4), (2, 1, 4, 3, 5), (2, 1, 4, 5, 3), (2, 1, 5, 3, 4), (2, 1, 5, 4, 3), (2, 3, 1, 4, 5), (2, 3, 1, 5, 4), (2, 3, 4, 1, 5), (2, 3, 4, 5, 1), (2, 3, 5, 1, 4), (2, 3, 5, 4, 1), (2, 4, 1, 3, 5), (2, 4, 1, 5, 3), (2, 4, 3, 1, 5), (2, 4, 3, 5, 1), (2, 4, 5, 1, 3), (2, 4, 5, 3, 1), (2, 5, 1, 3, 4), (2, 5, 1, 4, 3), (2, 5, 3, 1, 4), (2, 5, 3, 4, 1), (2, 5, 4, 1, 3), (2, 5, 4, 3, 1), (3, 1, 2, 4, 5), (3, 1, 2, 5, 4), (3, 1, 4, 2, 5), (3, 1, 4, 5, 2), (3, 1, 5, 2, 4), (3, 1, 5, 4, 2), (3, 2, 1, 4, 5), (3, 2, 1, 5, 4), (3, 2, 4, 1, 5), (3, 2, 4, 5, 1), (3, 2, 5, 1, 4), (3, 2, 5, 4, 1), (3, 4, 1, 2, 5), (3, 4, 1, 5, 2), (3, 4, 2, 1, 5), (3, 4, 2, 5, 1), (3, 4, 5, 1, 2), (3, 4, 5, 2, 1), (3, 5, 1, 2, 4), (3, 5, 1, 4, 2), (3, 5, 2, 1, 4), (3, 5, 2, 4, 1), (3, 5, 4, 1, 2), (3, 5, 4, 2, 1), (4, 1, 2, 3, 5), (4, 1, 2, 5, 3), (4, 1, 3, 2, 5), (4, 1, 3, 5, 2), (4, 1, 5, 2, 3), (4, 1, 5, 3, 2), (4, 2, 1, 3, 5), (4, 2, 1, 5, 3), (4, 2, 3, 1, 5), (4, 2, 3, 5, 1), (4, 2, 5, 1, 3), (4, 2, 5, 3, 1), (4, 3, 1, 2, 5), (4, 3, 1, 5, 2), (4, 3, 2, 1, 5), (4, 3, 2, 5, 1), (4, 3, 5, 1, 2), (4, 3, 5, 2, 1), (4, 5, 1, 2, 3), (4, 5, 1, 3, 2), (4, 5, 2, 1, 3), (4, 5, 2, 3, 1), (4, 5, 3, 1, 2), (4, 5, 3, 2, 1), (5, 1, 2, 3, 4), (5, 1, 2, 4, 3), (5, 1, 3, 2, 4), (5, 1, 3, 4, 2), (5, 1, 4, 2, 3), (5, 1, 4, 3, 2), (5, 2, 1, 3, 4), (5, 2, 1, 4, 3), (5, 2, 3, 1, 4), (5, 2, 3, 4, 1), (5, 2, 4, 1, 3), (5, 2, 4, 3, 1), (5, 3, 1, 2, 4), (5, 3, 1, 4, 2), (5, 3, 2, 1, 4), (5, 3, 2, 4, 1), (5, 3, 4, 1, 2), (5, 3, 4, 2, 1), (5, 4, 1, 2, 3), (5, 4, 1, 3, 2), (5, 4, 2, 1, 3), (5, 4, 2, 3, 1), (5, 4, 3, 1, 2), (5, 4, 3, 2, 1)]

    - name: Give me permutations of sets of three
      ansible.builtin.debug:
        msg: "{{ [1,2,3,4,5] | ansible.builtin.permutations(3) | list }}"
    # => [(1, 2, 3), (1, 2, 4), (1, 2, 5), (1, 3, 2), (1, 3, 4), (1, 3, 5), (1, 4, 2), (1, 4, 3), (1, 4, 5), (1, 5, 2), (1, 5, 3), (1, 5, 4), (2, 1, 3), (2, 1, 4), (2, 1, 5), (2, 3, 1), (2, 3, 4), (2, 3, 5), (2, 4, 1), (2, 4, 3), (2, 4, 5), (2, 5, 1), (2, 5, 3), (2, 5, 4), (3, 1, 2), (3, 1, 4), (3, 1, 5), (3, 2, 1), (3, 2, 4), (3, 2, 5), (3, 4, 1), (3, 4, 2), (3, 4, 5), (3, 5, 1), (3, 5, 2), (3, 5, 4), (4, 1, 2), (4, 1, 3), (4, 1, 5), (4, 2, 1), (4, 2, 3), (4, 2, 5), (4, 3, 1), (4, 3, 2), (4, 3, 5), (4, 5, 1), (4, 5, 2), (4, 5, 3), (5, 1, 2), (5, 1, 3), (5, 1, 4), (5, 2, 1), (5, 2, 3), (5, 2, 4), (5, 3, 1), (5, 3, 2), (5, 3, 4), (5, 4, 1), (5, 4, 2), (5, 4, 3)]

combinations
^^^^^^^^^^^^
Combinations always require a set size:

.. code-block:: yaml+jinja

    - name: Give me combinations for sets of two
      ansible.builtin.debug:
        msg: "{{ [1,2,3,4,5] | ansible.builtin.combinations(2) | list }}"
    # => [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]

Also see the :ref:`zip_filter`

products
^^^^^^^^
The product filter returns the `cartesian product <https://docs.python.org/3/library/itertools.html#itertools.product>`_ of the input iterables. This is roughly equivalent to nested for-loops in a generator expression.

.. code-block:: jinja

  {{ ['foo', 'bar'] | product(['com']) }}
  # => [('foo', 'com'), ('bar', 'com')]

For example Generate multiple hostnames:

.. code-block:: jinja

  {{ ['foo', 'bar'] | product(['com']) | map('join', '.') }}
  # => ['foo.com', 'bar.com']

.. json_query_filter:

Selecting JSON data: JSON queries
---------------------------------

To select a single element or a data subset from a complex data structure in JSON format (for example, Ansible facts), use the :ansplugin:`community.general.json_query#filter` filter.  The :ansplugin:`community.general.json_query#filter` filter lets you query a complex JSON structure and iterate over it using a loop structure.

.. note::

	This filter has migrated to the `community.general <https://galaxy.ansible.com/community/general>`_ collection. Follow the installation instructions to install that collection.


.. note:: You must manually install the **jmespath** dependency on the Ansible control node before using this filter. This filter is built upon **jmespath**, and you can use the same syntax. For examples, see `jmespath examples <https://jmespath.org/examples.html>`_.

Consider this data structure:

.. code-block:: json

    {
        "domain": {
            "cluster": [
                {
                    "name": "cluster1"
                },
                {
                    "name": "cluster2"
                }
            ],
            "server": [
                {
                    "name": "server11",
                    "cluster": "cluster1",
                    "port": "8080"
                },
                {
                    "name": "server12",
                    "cluster": "cluster1",
                    "port": "8090"
                },
                {
                    "name": "server21",
                    "cluster": "cluster2",
                    "port": "9080"
                },
                {
                    "name": "server22",
                    "cluster": "cluster2",
                    "port": "9090"
                }
            ],
            "library": [
                {
                    "name": "lib1",
                    "target": "cluster1"
                },
                {
                    "name": "lib2",
                    "target": "cluster2"
                }
            ]
        }
    }

To extract all clusters from this structure, you can use the following query:

.. code-block:: yaml+jinja

    - name: Display all cluster names
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.cluster[*].name') }}"

To extract all server names:

.. code-block:: yaml+jinja

    - name: Display all server names
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.server[*].name') }}"

To extract ports from cluster1:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
      vars:
        server_name_cluster1_query: "domain.server[?cluster=='cluster1'].port"

.. note:: You can use a variable to make the query more readable.

To print out the ports from cluster1 in a comma-separated string:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1 as a string
      ansible.builtin.debug:
        msg: "{{ domain_definition | community.general.json_query('domain.server[?cluster==`cluster1`].port') | join(', ') }}"

.. note:: In the example above, quoting literals using backticks avoids escaping quotes and maintains readability.

You can use YAML `single quote escaping <https://yaml.org/spec/current.html#id2534365>`_:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.server[?cluster==''cluster1''].port') }}"

.. note:: Escaping single quotes within single quotes in YAML is done by doubling the single quote.

To get a hash map with all ports and names of a cluster:

.. code-block:: yaml+jinja

    - name: Display all server ports and names from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
      vars:
        server_name_cluster1_query: "domain.server[?cluster=='cluster1'].{name: name, port: port}"

To extract ports from all clusters with the name starting with 'server1':

.. code-block:: yaml+jinja

    - name: Display ports from all clusters with the name starting with 'server1'
      ansible.builtin.debug:
        msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
      vars:
        server_name_query: "domain.server[?starts_with(name,'server1')].port"

To extract ports from all clusters with the name containing 'server1':

.. code-block:: yaml+jinja

    - name: Display ports from all clusters with the name containing 'server1'
      ansible.builtin.debug:
        msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
      vars:
        server_name_query: "domain.server[?contains(name,'server1')].port"

.. note:: while using ``starts_with`` and ``contains``, you have to use `` to_json | from_json `` filter for correct parsing of data structure.


Randomizing data
================

When you need a randomly generated value, use one of these filters.


.. _random_mac_filter:

Random MAC addresses
--------------------

.. versionadded:: 2.6

This filter can be used to generate a random MAC address from a string prefix.

.. note::

	This filter has migrated to the `community.general <https://galaxy.ansible.com/community/general>`_ collection. Follow the installation instructions to install that collection.

To get a random MAC address from a string prefix starting with '52:54:00':

.. code-block:: yaml+jinja

    "{{ '52:54:00' | community.general.random_mac }}"
    # => '52:54:00:ef:1c:03'

Note that if anything is wrong with the prefix string, the filter will issue an error.

 .. versionadded:: 2.9

As of Ansible version 2.9, you can also initialize the random number generator from a seed to create random-but-idempotent MAC addresses:

.. code-block:: yaml+jinja

    "{{ '52:54:00' | community.general.random_mac(seed=inventory_hostname) }}"


.. _random_filter_example:

Random items or numbers
-----------------------

The :ansplugin:`ansible.builtin.random#filter` filter in Ansible is an extension of the default Jinja2 random filter, and can be used to return a random item from a sequence of items or to generate a random number based on a range.

To get a random item from a list:

.. code-block:: yaml+jinja

    "{{ ['a','b','c'] | random }}"
    # => 'c'

To get a random number between 0 (inclusive) and a specified integer (exclusive):

.. code-block:: yaml+jinja

    "{{ 60 | random }} * * * * root /script/from/cron"
    # => '21 * * * * root /script/from/cron'

To get a random number from 0 to 100 but in steps of 10:

.. code-block:: jinja

    {{ 101 | random(step=10) }}
    # => 70

To get a random number from 1 to 100 but in steps of 10:

.. code-block:: jinja

    {{ 101 | random(1, 10) }}
    # => 31
    {{ 101 | random(start=1, step=10) }}
    # => 51

You can initialize the random number generator from a seed to create random-but-idempotent numbers:

.. code-block:: jinja

    "{{ 60 | random(seed=inventory_hostname) }} * * * * root /script/from/cron"

Shuffling a list
----------------

The :ansplugin:`ansible.builtin.shuffle#filter` filter randomizes an existing list, giving a different order for every invocation.

To get a random list from an existing  list:

.. code-block:: jinja

    {{ ['a','b','c'] | shuffle }}
    # => ['c','a','b']
    {{ ['a','b','c'] | shuffle }}
    # => ['b','c','a']

You can initialize the shuffle generator from a seed to generate a random-but-idempotent order:

.. code-block:: jinja

    {{ ['a','b','c'] | shuffle(seed=inventory_hostname) }}
    # => ['b','a','c']

The shuffle filter returns a list whenever possible. If you use it with a non 'listable' item, the filter does nothing.


.. _list_filters:

Managing list variables
=======================

You can search for the minimum or maximum value in a list, or flatten a multi-level list.

To get the minimum value from the list of numbers:

.. code-block:: jinja

    {{ [3, 4, 2] | min }}
    # => 2

.. versionadded:: 2.11

To get the minimum value in a list of objects:

.. code-block:: jinja

    {{ [{'val': 1}, {'val': 2}] | min(attribute='val') }}
    # => {'val': 1}

To get the maximum value from a list of numbers:

.. code-block:: jinja

    {{ [3, 4, 2] | max }}
    # => 4

.. versionadded:: 2.11

To get the maximum value in a list of objects:

.. code-block:: jinja

    {{ [{'val': 1}, {'val': 2}] | max(attribute='val') }}
    # => {'val': 2}

.. versionadded:: 2.5

Flatten a list (same thing the `flatten` lookup does):

.. code-block:: jinja

    {{ [3, [4, 2] ] | flatten }}
    # => [3, 4, 2]

Flatten only the first level of a list (akin to the `items` lookup):

.. code-block:: jinja

    {{ [3, [4, [2]] ] | flatten(levels=1) }}
    # => [3, 4, [2]]


.. versionadded:: 2.11

Preserve nulls in a list (flatten removes them by default):

.. code-block:: jinja

    {{ [3, None, [4, [2]] ] | flatten(levels=1, skip_nulls=False) }}
    # => [3, None, 4, [2]]

Create a list from a list repeated N times:

.. code-block:: jinja

    {{ 3*[1, 2, 3, "foo"] }}
    # => [1, 2, 3, 'foo', 1, 2, 3, 'foo', 1, 2, 3, 'foo']



.. _set_theory_filters:

Selecting from sets or lists (set theory)
=========================================

You can select or combine items from sets or lists. Note, multisets are currently not supported and all of the following filters imply uniqueness. That means that duplicate elements are removed from the result.

.. versionadded:: 1.4

To get a unique set from a list:

.. code-block:: jinja

    # list1: [1, 2, 5, 1, 3, 4, 10]
    {{ list1 | unique }}
    # => [1, 2, 5, 3, 4, 10]

To get a union (with duplicate elements removed) of two lists:

.. code-block:: jinja

    # list1: [1, 2, 5, 1, 3, 4, 10]
    # list2: [1, 2, 3, 4, 5, 11, 99]
    {{ list1 | union(list2) }}
    # => [1, 2, 3, 4, 5, 99, 10, 11]

To get the intersection of 2 lists (unique list of all items in both):

.. code-block:: jinja

    # list1: [1, 2, 5, 3, 4, 10]
    # list2: [1, 2, 3, 4, 5, 11, 99]
    {{ list1 | intersect(list2) }}
    # => [1, 2, 3, 4, 5]

To get the difference of 2 lists (items in 1 that don't exist in 2):

.. code-block:: jinja

    # list1: [1, 2, 5, 1, 3, 4, 10]
    # list2: [1, 2, 3, 4, 5, 11, 99]
    {{ list1 | difference(list2) }}
    # => [10]

To get the symmetric difference of 2 lists (items exclusive to each list):

.. code-block:: jinja

    # list1: [1, 2, 5, 1, 3, 4, 10]
    # list2: [1, 2, 3, 4, 5, 11, 99]
    {{ list1 | symmetric_difference(list2) }}
    # => [99, 10, 11]

.. _math_stuff:

Calculating numbers (math)
==========================

.. versionadded:: 1.9

You can calculate logs, powers, and roots of numbers with Ansible filters. Jinja2 provides other mathematical functions like abs() and round().

Get the logarithm (default is e):

.. code-block:: jinja

    {{ 8 | log }}
    # => 2.0794415416798357

Get the base 10 logarithm:

.. code-block:: jinja

    {{ 8 | log(10) }}
    # => 0.9030899869919435

Give me the power of 2! (or 5):

.. code-block:: jinja

    {{ 8 | pow(5) }}
    # => 32768.0

Square root, or the 5th:

.. code-block:: jinja

    {{ 8 | root }}
    # => 2.8284271247461903

    {{ 8 | root(5) }}
    # => 1.5157165665103982


Managing network interactions
=============================

These filters help you with common network tasks.

.. note::

	These filters have migrated to the `ansible.utils <https://galaxy.ansible.com/ansible/utils>`_ collection. Follow the installation instructions to install that collection.

.. _ipaddr_filter:

IP address filters
------------------

.. versionadded:: 1.9

To test if a string is a valid IP address:

.. code-block:: jinja

  {{ myvar | ansible.utils.ipaddr }}

You can also require a specific IP protocol version:

.. code-block:: jinja

  {{ myvar | ansible.utils.ipv4 }}
  {{ myvar | ansible.utils.ipv6 }}

IP address filter can also be used to extract specific information from an IP
address. For example, to get the IP address itself from a CIDR, you can use:

.. code-block:: jinja

  {{ '192.0.2.1/24' | ansible.utils.ipaddr('address') }}
  # => 192.0.2.1

More information about :ansplugin:`ansible.utils.ipaddr#filter` filter and complete usage guide can be found
in :ref:`plugins_in_ansible.utils`.

.. _network_filters:

Network CLI filters
-------------------

.. versionadded:: 2.4

To convert the output of a network device CLI command into structured JSON
output, use the :ansplugin:`ansible.netcommon.parse_cli#filter` filter:

.. code-block:: yaml+jinja

    {{ output | ansible.netcommon.parse_cli('path/to/spec') }}

The :ansplugin:`ansible.netcommon.parse_cli#filter` filter will load the spec file and pass the command output
through it, returning JSON output. The YAML spec file defines how to parse the CLI output.

The spec file should be valid formatted YAML.  It defines how to parse the CLI
output and return JSON data.  Below is an example of a valid spec file that
will parse the output from the ``show vlan`` command.

.. code-block:: yaml+jinja

   ---
   vars:
     vlan:
       vlan_id: "{{ item.vlan_id }}"
       name: "{{ item.name }}"
       enabled: "{{ item.state != 'act/lshut' }}"
       state: "{{ item.state }}"

   keys:
     vlans:
       value: "{{ vlan }}"
       items: "^(?P<vlan_id>\\d+)\\s+(?P<name>\\w+)\\s+(?P<state>active|act/lshut|suspended)"
     state_static:
       value: present


The spec file above will return a JSON data structure that is a list of hashes
with the parsed VLAN information.

The same command could be parsed into a hash by using the key and values
directives.  Here is an example of how to parse the output into a hash
value using the same ``show vlan`` command.

.. code-block:: yaml+jinja

   ---
   vars:
     vlan:
       key: "{{ item.vlan_id }}"
       values:
         vlan_id: "{{ item.vlan_id }}"
         name: "{{ item.name }}"
         enabled: "{{ item.state != 'act/lshut' }}"
         state: "{{ item.state }}"

   keys:
     vlans:
       value: "{{ vlan }}"
       items: "^(?P<vlan_id>\\d+)\\s+(?P<name>\\w+)\\s+(?P<state>active|act/lshut|suspended)"
     state_static:
       value: present

Another common use case for parsing CLI commands is to break a large command
into blocks that can be parsed.  This can be done using the ``start_block`` and
``end_block`` directives to break the command into blocks that can be parsed.

.. code-block:: yaml+jinja

   ---
   vars:
     interface:
       name: "{{ item[0].match[0] }}"
       state: "{{ item[1].state }}"
       mode: "{{ item[2].match[0] }}"

   keys:
     interfaces:
       value: "{{ interface }}"
       start_block: "^Ethernet.*$"
       end_block: "^$"
       items:
         - "^(?P<name>Ethernet\\d\\/\\d*)"
         - "admin state is (?P<state>.+),"
         - "Port mode is (.+)"


The example above will parse the output of ``show interface`` into a list of
hashes.

The network filters also support parsing the output of a CLI command using the
TextFSM library.  To parse the CLI output with TextFSM use the following
filter:

.. code-block:: jinja

  {{ output.stdout[0] | ansible.netcommon.parse_cli_textfsm('path/to/fsm') }}

Use of the TextFSM filter requires the TextFSM library to be installed.

Network XML filters
-------------------

.. versionadded:: 2.5

To convert the XML output of a network device command into structured JSON
output, use the :ansplugin:`ansible.netcommon.parse_xml#filter` filter:

.. code-block:: jinja

  {{ output | ansible.netcommon.parse_xml('path/to/spec') }}

The :ansplugin:`ansible.netcommon.parse_xml#filter` filter will load the spec file and pass the command output
through formatted as JSON.

The spec file should be valid formatted YAML. It defines how to parse the XML
output and return JSON data.

Below is an example of a valid spec file that
will parse the output from the ``show vlan | display xml`` command.

.. code-block:: yaml+jinja

   ---
   vars:
     vlan:
       vlan_id: "{{ item.vlan_id }}"
       name: "{{ item.name }}"
       desc: "{{ item.desc }}"
       enabled: "{{ item.state.get('inactive') != 'inactive' }}"
       state: "{% if item.state.get('inactive') == 'inactive'%} inactive {% else %} active {% endif %}"

   keys:
     vlans:
       value: "{{ vlan }}"
       top: configuration/vlans/vlan
       items:
         vlan_id: vlan-id
         name: name
         desc: description
         state: ".[@inactive='inactive']"


The spec file above will return a JSON data structure that is a list of hashes
with the parsed VLAN information.

The same command could be parsed into a hash by using the key and values
directives.  Here is an example of how to parse the output into a hash
value using the same ``show vlan | display xml`` command.

.. code-block:: yaml+jinja

   ---
   vars:
     vlan:
       key: "{{ item.vlan_id }}"
       values:
           vlan_id: "{{ item.vlan_id }}"
           name: "{{ item.name }}"
           desc: "{{ item.desc }}"
           enabled: "{{ item.state.get('inactive') != 'inactive' }}"
           state: "{% if item.state.get('inactive') == 'inactive'%} inactive {% else %} active {% endif %}"

   keys:
     vlans:
       value: "{{ vlan }}"
       top: configuration/vlans/vlan
       items:
         vlan_id: vlan-id
         name: name
         desc: description
         state: ".[@inactive='inactive']"


The value of ``top`` is the XPath relative to the XML root node.
In the example, XML output given below, the value of ``top`` is ``configuration/vlans/vlan``,
which is an XPath expression relative to the root node (<rpc-reply>).
``configuration`` in the value of ``top`` is the outermost container node, and ``vlan``
is the innermost container node.

``items`` is a dictionary of key-value pairs that map user-defined names to XPath expressions
that select elements. The Xpath expression is relative to the value of the XPath value contained in ``top``.
For example, the ``vlan_id`` in the spec file is a user-defined name and its value ``vlan-id`` is the
relative to the value of XPath in ``top``

Attributes of XML tags can be extracted using XPath expressions. The value of ``state`` in the spec
is an XPath expression used to get the attributes of the ``vlan`` tag in output XML.:

.. code-block:: none

    <rpc-reply>
      <configuration>
        <vlans>
          <vlan inactive="inactive">
           <name>vlan-1</name>
           <vlan-id>200</vlan-id>
           <description>This is vlan-1</description>
          </vlan>
        </vlans>
      </configuration>
    </rpc-reply>

.. note::
  For more information on supported XPath expressions, see `XPath Support <https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support>`_.

Network VLAN filters
--------------------

.. versionadded:: 2.8

Use the :ansplugin:`ansible.netcommon.vlan_parser#filter` filter to transform an unsorted list of VLAN integers into a
sorted string list of integers according to IOS-like VLAN list rules. This list has the following properties:

* Vlans are listed in ascending order.
* Three or more consecutive VLANs are listed with a dash.
* The first line of the list can be first_line_len characters long.
* Subsequent list lines can be other_line_len characters.

To sort a VLAN list:

.. code-block:: jinja

    {{ [3003, 3004, 3005, 100, 1688, 3002, 3999] | ansible.netcommon.vlan_parser }}

This example renders the following sorted list:

.. code-block:: text

    ['100,1688,3002-3005,3999']


Another example Jinja template:

.. code-block:: jinja

    {% set parsed_vlans = vlans | ansible.netcommon.vlan_parser %}
    switchport trunk allowed vlan {{ parsed_vlans[0] }}
    {% for i in range (1, parsed_vlans | count) %}
    switchport trunk allowed vlan add {{ parsed_vlans[i] }}
    {% endfor %}

This allows for the dynamic generation of VLAN lists on a Cisco IOS tagged interface. You can store an exhaustive raw list of the exact VLANs required for an interface and then compare that to the parsed IOS output that would actually be generated for the configuration.


.. _hash_filters:

Hashing and encrypting strings and passwords
==============================================

.. versionadded:: 1.9

To get the sha1 hash of a string:

.. code-block:: jinja

    {{ 'test1' | hash('sha1') }}
    # => "b444ac06613fc8d63795be9ad0beaf55011936ac"

To get the md5 hash of a string:

.. code-block:: jinja

    {{ 'test1' | hash('md5') }}
    # => "5a105e8b9d40e1329780d62ea2265d8a"

Get a string checksum:

.. code-block:: jinja

    {{ 'test2' | checksum }}
    # => "109f4b3c50d7b0df729d299bc6f8e9ef9066971f"

Other hashes (platform dependent):

.. code-block:: jinja

    {{ 'test2' | hash('blowfish') }}

To get a sha512 password hash (random salt):

.. code-block:: jinja

    {{ 'passwordsaresecret' | password_hash('sha512') }}
    # => "$6$UIv3676O/ilZzWEE$ktEfFF19NQPF2zyxqxGkAceTnbEgpEKuGBtk6MlU4v2ZorWaVQUMyurgmHCh2Fr4wpmQ/Y.AlXMJkRnIS4RfH/"

To get a sha256 password hash with a specific salt:

.. code-block:: jinja

    {{ 'secretpassword' | password_hash('sha256', 'mysecretsalt') }}
    # => "$5$mysecretsalt$ReKNyDYjkKNqRVwouShhsEqZ3VOE8eoVO4exihOfvG4"

An idempotent method to generate unique hashes per system is to use a salt that is consistent between runs:

.. code-block:: jinja

    {{ 'secretpassword' | password_hash('sha512', 65534 | random(seed=inventory_hostname) | string) }}
    # => "$6$43927$lQxPKz2M2X.NWO.gK.t7phLwOKQMcSq72XxDZQ0XzYV6DlL1OD72h417aj16OnHTGxNzhftXJQBcjbunLEepM0"

Hash types available depend on the control system running Ansible, :ansplugin:`ansible.builtin.hash#filter` depends on `hashlib <https://docs.python.org/3.8/library/hashlib.html>`_, :ansplugin:`ansible.builtin.password_hash#filter` depends on `passlib <https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html>`_. The `crypt <https://docs.python.org/3.8/library/crypt.html>`_ is used as a fallback if ``passlib`` is not installed.

.. versionadded:: 2.7

Some hash types allow providing a rounds parameter:

.. code-block:: jinja

    {{ 'secretpassword' | password_hash('sha256', 'mysecretsalt', rounds=10000) }}
    # => "$5$rounds=10000$mysecretsalt$Tkm80llAxD4YHll6AgNIztKn0vzAACsuuEfYeGP7tm7"

The filter `password_hash` produces different results depending on whether you installed `passlib` or not.

To ensure idempotency, specify `rounds` to be neither `crypt`'s nor `passlib`'s default, which is `5000` for `crypt` and a variable value (`535000` for sha256, `656000` for sha512) for `passlib`:

.. code-block:: jinja

    {{ 'secretpassword' | password_hash('sha256', 'mysecretsalt', rounds=5001) }}
    # => "$5$rounds=5001$mysecretsalt$wXcTWWXbfcR8er5IVf7NuquLvnUA6s8/qdtOhAZ.xN."

Hash type 'blowfish' (BCrypt) provides the facility to specify the version of the BCrypt algorithm.

.. code-block:: jinja

    {{ 'secretpassword' | password_hash('blowfish', '1234567890123456789012', ident='2b') }}
    # => "$2b$12$123456789012345678901uuJ4qFdej6xnWjOQT.FStqfdoY8dYUPC"

.. note::
    The parameter is only available for `blowfish (BCrypt) <https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html#passlib.hash.bcrypt>`_.
    Other hash types will simply ignore this parameter.
    Valid values for this parameter are: ['2', '2a', '2y', '2b']

.. versionadded:: 2.12

You can also use the Ansible :ansplugin:`ansible.builtin.vault#filter` filter to encrypt data:

.. code-block:: yaml+jinja

  # simply encrypt my key in a vault
  vars:
    myvaultedkey: "{{ keyrawdata|vault(passphrase) }}"

  tasks:
  - name: save templated vaulted data
    template: src=dump_template_data.j2 dest=/some/key/vault.txt
    vars:
      mysalt: '{{ 2**256|random(seed=inventory_hostname) }}'
      template_data: '{{ secretdata|vault(vaultsecret, salt=mysalt) }}'


And then decrypt it using the unvault filter:

.. code-block:: yaml+jinja

  # simply decrypt my key from a vault
  vars:
    mykey: "{{ myvaultedkey|unvault(passphrase) }}"

  tasks:
  - name: save templated unvaulted data
    template: src=dump_template_data.j2 dest=/some/key/clear.txt
    vars:
      template_data: '{{ secretdata|unvault(vaultsecret) }}'


.. _other_useful_filters:

Manipulating text
=================

Several filters work with text, including URLs, file names, and path names.

.. _comment_filter:

Adding comments to files
------------------------

The :ansplugin:`ansible.builtin.comment#filter` filter lets you create comments in a file from text in a template, with a variety of comment styles. By default, Ansible uses ``#`` to start a comment line and adds a blank comment line above and below your comment text. For example the following:

.. code-block:: jinja

    {{ "Plain style (default)" | comment }}

produces this output:

.. code-block:: text

    #
    # Plain style (default)
    #

Ansible offers styles for comments in C (``//...``), C block
(``/*...*/``), Erlang (``%...``) and XML (``<!--...-->``):

.. code-block:: jinja

    {{ "C style" | comment('c') }}
    {{ "C block style" | comment('cblock') }}
    {{ "Erlang style" | comment('erlang') }}
    {{ "XML style" | comment('xml') }}

You can define a custom comment character. This filter:

.. code-block:: jinja

  {{ "My Special Case" | comment(decoration="! ") }}

produces:

.. code-block:: text

  !
  ! My Special Case
  !

You can fully customize the comment style:

.. code-block:: jinja

    {{ "Custom style" | comment('plain', prefix='#######\n#', postfix='#\n#######\n   ###\n    #') }}

That creates the following output:

.. code-block:: text

    #######
    #
    # Custom style
    #
    #######
       ###
        #

URLEncode Variables
-------------------

The ``urlencode`` filter quotes data for use in a URL path or query using UTF-8:

.. code-block:: jinja

    {{ 'Trollhättan' | urlencode }}
    # => 'Trollh%C3%A4ttan'

Splitting URLs
--------------

.. versionadded:: 2.4

The :ansplugin:`ansible.builtin.urlsplit#filter` filter extracts the fragment, hostname, netloc, password, path, port, query, scheme, and username from an URL. With no arguments, returns a dictionary of all the fields:

.. code-block:: jinja

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('hostname') }}
    # => 'www.acme.com'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('netloc') }}
    # => 'user:password@www.acme.com:9000'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('username') }}
    # => 'user'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('password') }}
    # => 'password'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('path') }}
    # => '/dir/index.html'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('port') }}
    # => '9000'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('scheme') }}
    # => 'http'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('query') }}
    # => 'query=term'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit('fragment') }}
    # => 'fragment'

    {{ "http://user:password@www.acme.com:9000/dir/index.html?query=term#fragment" | urlsplit }}
    # =>
    #   {
    #       "fragment": "fragment",
    #       "hostname": "www.acme.com",
    #       "netloc": "user:password@www.acme.com:9000",
    #       "password": "password",
    #       "path": "/dir/index.html",
    #       "port": 9000,
    #       "query": "query=term",
    #       "scheme": "http",
    #       "username": "user"
    #   }

Searching strings with regular expressions
------------------------------------------

To search in a string or extract parts of a string with a regular expression, use the :ansplugin:`ansible.builtin.regex_search#filter` filter:

.. code-block:: jinja

    # Extracts the database name from a string
    {{ 'server1/database42' | regex_search('database[0-9]+') }}
    # => 'database42'

    # Example for a case insensitive search in multiline mode
    {{ 'foo\nBAR' | regex_search('^bar', multiline=True, ignorecase=True) }}
    # => 'BAR'

    # Example for a case insensitive search in multiline mode using inline regex flags
    {{ 'foo\nBAR' | regex_search('(?im)^bar') }}
    # => 'BAR'

    # Extracts server and database id from a string
    {{ 'server1/database42' | regex_search('server([0-9]+)/database([0-9]+)', '\\1', '\\2') }}
    # => ['1', '42']

    # Extracts dividend and divisor from a division
    {{ '21/42' | regex_search('(?P<dividend>[0-9]+)/(?P<divisor>[0-9]+)', '\\g<dividend>', '\\g<divisor>') }}
    # => ['21', '42']

To extract all occurrences of regex matches in a string, use the :ansplugin:`ansible.builtin.regex_findall#filter` filter:

.. code-block:: jinja

    # Returns a list of all IPv4 addresses in the string
    {{ 'Some DNS servers are 8.8.8.8 and 8.8.4.4' | regex_findall('\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b') }}
    # => ['8.8.8.8', '8.8.4.4']

    # Returns all lines that end with "ar"
    {{ 'CAR\ntar\nfoo\nbar\n' | regex_findall('^.ar$', multiline=True, ignorecase=True) }}
    # => ['CAR', 'tar', 'bar']

    # Returns all lines that end with "ar" using inline regex flags for multiline and ignorecase
    {{ 'CAR\ntar\nfoo\nbar\n' | regex_findall('(?im)^.ar$') }}
    # => ['CAR', 'tar', 'bar']

To replace text in a string with regex, use the :ansplugin:`ansible.builtin.regex_replace#filter` filter:

.. code-block:: jinja

    # Convert "ansible" to "able"
    {{ 'ansible' | regex_replace('^a.*i(.*)$', 'a\\1') }}
    # => 'able'

    # Convert "foobar" to "bar"
    {{ 'foobar' | regex_replace('^f.*o(.*)$', '\\1') }}
    # => 'bar'

    # Convert "localhost:80" to "localhost, 80" using named groups
    {{ 'localhost:80' | regex_replace('^(?P<host>.+):(?P<port>\\d+)$', '\\g<host>, \\g<port>') }}
    # => 'localhost, 80'

    # Convert "localhost:80" to "localhost"
    {{ 'localhost:80' | regex_replace(':80') }}
    # => 'localhost'

    # Comment all lines that end with "ar"
    {{ 'CAR\ntar\nfoo\nbar\n' | regex_replace('^(.ar)$', '#\\1', multiline=True, ignorecase=True) }}
    # => '#CAR\n#tar\nfoo\n#bar\n'

    # Comment all lines that end with "ar" using inline regex flags for multiline and ignorecase
    {{ 'CAR\ntar\nfoo\nbar\n' | regex_replace('(?im)^(.ar)$', '#\\1') }}
    # => '#CAR\n#tar\nfoo\n#bar\n'

.. note::
   If you want to match the whole string and you are using ``*`` make sure to always wraparound your regular expression with the start/end anchors. For example ``^(.*)$`` will always match only one result, while ``(.*)`` on some Python versions will match the whole string and an empty string at the end, which means it will make two replacements:

.. code-block:: jinja

      # add "https://" prefix to each item in a list
      GOOD:
      {{ hosts | map('regex_replace', '^(.*)$', 'https://\\1') | list }}
      {{ hosts | map('regex_replace', '(.+)', 'https://\\1') | list }}
      {{ hosts | map('regex_replace', '^', 'https://') | list }}

      BAD:
      {{ hosts | map('regex_replace', '(.*)', 'https://\\1') | list }}

      # append ':80' to each item in a list
      GOOD:
      {{ hosts | map('regex_replace', '^(.*)$', '\\1:80') | list }}
      {{ hosts | map('regex_replace', '(.+)', '\\1:80') | list }}
      {{ hosts | map('regex_replace', '$', ':80') | list }}

      BAD:
      {{ hosts | map('regex_replace', '(.*)', '\\1:80') | list }}

.. note::
   Prior to ansible 2.0, if :ansplugin:`ansible.builtin.regex_replace#filter` filter was used with variables inside YAML arguments (as opposed to simpler 'key=value' arguments), then you needed to escape backreferences (for example, ``\\1``) with 4 backslashes (``\\\\``) instead of 2 (``\\``).

.. versionadded:: 2.0

To escape special characters within a standard Python regex, use the :ansplugin:`ansible.builtin.regex_escape#filter` filter (using the default :ansopt:`ansible.builtin.regex_escape#filter:re_type='python'` option):

.. code-block:: jinja

    # convert '^f.*o(.*)$' to '\^f\.\*o\(\.\*\)\$'
    {{ '^f.*o(.*)$' | regex_escape() }}

.. versionadded:: 2.8

To escape special characters within a POSIX basic regex, use the :ansplugin:`ansible.builtin.regex_escape#filter` filter with the :ansopt:`ansible.builtin.regex_escape#filter:re_type='posix_basic'` option:

.. code-block:: jinja

    # convert '^f.*o(.*)$' to '\^f\.\*o(\.\*)\$'
    {{ '^f.*o(.*)$' | regex_escape('posix_basic') }}


Managing file names and path names
----------------------------------

To get the last name of a file path, like 'foo.txt' out of '/etc/asdf/foo.txt':

.. code-block:: jinja

    {{ path | basename }}

To get the last name of a Windows style file path (new in version 2.0):

.. code-block:: jinja

    {{ path | win_basename }}

To separate the Windows drive letter from the rest of a file path (new in version 2.0):

.. code-block:: jinja

    {{ path | win_splitdrive }}

To get only the Windows drive letter:

.. code-block:: jinja

    {{ path | win_splitdrive | first }}

To get the rest of the path without the drive letter:

.. code-block:: jinja

    {{ path | win_splitdrive | last }}

To get the directory from a path:

.. code-block:: jinja

    {{ path | dirname }}

To get the directory from a Windows path (new version 2.0):

.. code-block:: jinja

    {{ path | win_dirname }}

To expand a path containing a tilde (`~`) character (new in version 1.5):

.. code-block:: jinja

    {{ path | expanduser }}

To expand a path containing environment variables:

.. code-block:: jinja

    {{ path | expandvars }}

.. note:: `expandvars` expands local variables; using it on remote paths can lead to errors.

.. versionadded:: 2.6

To get the real path of a link (new in version 1.8):

.. code-block:: jinja

    {{ path | realpath }}

To get the relative path of a link, from a start point (new in version 1.7):

.. code-block:: jinja

    {{ path | relpath('/etc') }}

To get the root and extension of a path or file name (new in version 2.0):

.. code-block:: jinja

    # with path == 'nginx.conf' the return would be ('nginx', '.conf')
    {{ path | splitext }}

The :ansplugin:`ansible.builtin.splitext#filter` filter always returns a pair of strings. The individual components can be accessed by using the ``first`` and ``last`` filters:

.. code-block:: jinja

    # with path == 'nginx.conf' the return would be 'nginx'
    {{ path | splitext | first }}

    # with path == 'nginx.conf' the return would be '.conf'
    {{ path | splitext | last }}

To join one or more path components:

.. code-block:: jinja

    {{ ('/etc', path, 'subdir', file) | path_join }}

.. versionadded:: 2.10

Manipulating strings
====================

To add quotes for shell usage:

.. code-block:: yaml+jinja

    - name: Run a shell command
      ansible.builtin.shell: echo {{ string_value | quote }}

(Documentation: :ansplugin:`ansible.builtin.quote#filter`)

To concatenate a list into a string:

.. code-block:: jinja

    {{ list | join(" ") }}

To split a string into a list:

.. code-block:: jinja

    {{ csv_string | split(",") }}

.. versionadded:: 2.11

To work with Base64 encoded strings:

.. code-block:: jinja

    {{ encoded | b64decode }}
    {{ decoded | string | b64encode }}

(Documentation: :ansplugin:`ansible.builtin.b64encode#filter`)

As of version 2.6, you can define the type of encoding to use, the default is ``utf-8``:

.. code-block:: jinja

    {{ encoded | b64decode(encoding='utf-16-le') }}
    {{ decoded | string | b64encode(encoding='utf-16-le') }}

(Documentation: :ansplugin:`ansible.builtin.b64decode#filter`)

.. note:: The ``string`` filter is only required for Python 2 and ensures that the text to encode is a unicode string. Without that filter before b64encode the wrong value will be encoded.

.. note:: The return value of b64decode is a string.  If you decrypt a binary blob using b64decode and then try to use it (for example by using :ref:`copy <copy_module>` to write it to a file) you will most likely find that your binary has been corrupted.  If you need to take a base64 encoded binary and write it to disk, it is best to use the system ``base64`` command with the :ref:`shell module <shell_module>`, piping in the encoded data using the ``stdin`` parameter. For example: ``shell: cmd="base64 --decode > myfile.bin" stdin="{{ encoded }}"``

.. versionadded:: 2.6

Managing UUIDs
==============

To create a namespaced UUIDv5:

.. code-block:: jinja

    {{ string | to_uuid(namespace='11111111-2222-3333-4444-555555555555') }}

.. versionadded:: 2.10

To create a namespaced UUIDv5 using the default Ansible namespace '361E6D51-FAEC-444A-9079-341386DA8E2E':

.. code-block:: jinja

    {{ string | to_uuid }}

.. versionadded:: 1.9

To make use of one attribute from each item in a list of complex variables, use the :func:`Jinja2 map filter <jinja2:jinja-filters.map>`:

.. code-block:: jinja

    # get a comma-separated list of the mount points (for example, "/,/mnt/stuff") on a host
    {{ ansible_mounts | map(attribute='mount') | join(',') }}

Handling dates and times
========================

To get a date object from a string use the `to_datetime` filter:

.. code-block:: jinja

    # Get the total amount of seconds between two dates. Default date format is %Y-%m-%d %H:%M:%S but you can pass your own format
    {{ (("2016-08-14 20:00:12" | to_datetime) - ("2015-12-25" | to_datetime('%Y-%m-%d'))).total_seconds()  }}

    # Get remaining seconds after delta has been calculated. NOTE: This does NOT convert years, days, hours, and so on to seconds. For that, use total_seconds()
    {{ (("2016-08-14 20:00:12" | to_datetime) - ("2016-08-14 18:00:00" | to_datetime)).seconds  }}
    # This expression evaluates to "12" and not "132". Delta is 2 hours, 12 seconds

    # get amount of days between two dates. This returns only the number of days and discards remaining hours, minutes, and seconds
    {{ (("2016-08-14 20:00:12" | to_datetime) - ("2015-12-25" | to_datetime('%Y-%m-%d'))).days  }}

.. note:: For a full list of format codes for working with Python date format strings, see the `python datetime documentation <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior>`_.

.. versionadded:: 2.4

To format a date using a string (like with the shell date command), use the "strftime" filter:

.. code-block:: jinja

    # Display year-month-day
    {{ '%Y-%m-%d' | strftime }}
    # => "2021-03-19"

    # Display hour:min:sec
    {{ '%H:%M:%S' | strftime }}
    # => "21:51:04"

    # Use ansible_date_time.epoch fact
    {{ '%Y-%m-%d %H:%M:%S' | strftime(ansible_date_time.epoch) }}
    # => "2021-03-19 21:54:09"

    # Use arbitrary epoch value
    {{ '%Y-%m-%d' | strftime(0) }}          # => 1970-01-01
    {{ '%Y-%m-%d' | strftime(1441357287) }} # => 2015-09-04

.. versionadded:: 2.13

strftime takes an optional utc argument, defaulting to False, meaning times are in the local timezone:

.. code-block:: jinja

    {{ '%H:%M:%S' | strftime }}           # time now in local timezone
    {{ '%H:%M:%S' | strftime(utc=True) }} # time now in UTC

.. note:: To get all string possibilities, check https://docs.python.org/3/library/time.html#time.strftime

Getting Kubernetes resource names
=================================

.. note::

	These filters have migrated to the `kubernetes.core <https://galaxy.ansible.com/kubernetes/core>`_ collection. Follow the installation instructions to install that collection.

Use the "k8s_config_resource_name" filter to obtain the name of a Kubernetes ConfigMap or Secret,
including its hash:

.. code-block:: yaml+jinja

    {{ configmap_resource_definition | kubernetes.core.k8s_config_resource_name }}

This can then be used to reference hashes in Pod specifications:

.. code-block:: yaml+jinja

    my_secret:
      kind: Secret
      metadata:
        name: my_secret_name

    deployment_resource:
      kind: Deployment
      spec:
        template:
          spec:
            containers:
            - envFrom:
                - secretRef:
                    name: {{ my_secret | kubernetes.core.k8s_config_resource_name }}

.. versionadded:: 2.8

.. _PyYAML library: https://pyyaml.org/

.. _PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation


.. seealso::

   :ref:`about_playbooks`
       An introduction to playbooks
   :ref:`playbooks_conditionals`
       Conditional statements in playbooks
   :ref:`playbooks_variables`
       All about variables
   :ref:`playbooks_loops`
       Looping in playbooks
   :ref:`playbooks_reuse_roles`
       Playbook organization by roles
   :ref:`tips_and_tricks`
       Tips and tricks for playbooks
   :ref:`Communication<communication>`
       Got questions? Need help? Want to share your ideas? Visit the Ansible communication guide
   `Python 3 Regular expression operations <https://docs.python.org/3/library/re.html>`_
       How to use inline regular expression flags
