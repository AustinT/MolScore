import os
import re
import json
import inspect

import streamlit as st

from molscore import utils
import molscore.scaffold_memory as scaffold_memory
import molscore.scoring_functions as scoring_functions

# Set session variables, persistent on re-runs
ss = st.session_state
if 'configs' not in ss:
    ss.input_path = 'configs'
if 'n_sf' not in ss:
    ss.n_sf=1
if 'n_sp' not in ss:
    ss.n_sp=1
if 'maxmin' not in ss:
    ss.maxmin=False
if 'pidgin_docstring' not in ss:
    ss.pidgin_docstring=False


# ----- Functions -----
def st_file_selector(st_placeholder, key, path='.', label='Please, select a file/folder...', counter=1):
    """
    Code for a file selector widget which remembers where you are...
    """
    # get base path (directory)
    base_path = '.' if (path is None) or (path == '') else path
    base_path = base_path if os.path.isdir(
        base_path) else os.path.dirname(base_path)
    base_path = '.' if (base_path is None) or (base_path == '') else base_path
    # list files in base path directory
    files = os.listdir(base_path)
    files.insert(0, '..')
    files.insert(0, '.')
    selected_file = st_placeholder.selectbox(
        label=label, options=files, key=key)
    selected_path = os.path.normpath(os.path.join(base_path, selected_file))
    if selected_file == '.':
        return selected_path
    if os.path.isdir(selected_path):
        # ----
        counter += 1
        key = key + str(counter)
        # ----
        selected_path = st_file_selector(st_placeholder=st_placeholder,
                                         path=selected_path, label=label,
                                         key=key, counter=counter)
    return os.path.abspath(selected_path)


def type2widget(ptype, label, key, default=None, options=None):
    """
    Infer widget based on parameter datatype
    :param ptype: Parameter data type
    :param label: Description for the widget to write
    :param key: Unique key for widget
    :param default: Default parameter value
    :param options: If present use selectbox
    :return:
    """
    if options is not None:
        widget = st.selectbox(
            label=label,
            options=options,
            index=options.index(default) if default in options else 0,
            key=key
        )
    else:
        if ptype == str:
            widget = st.text_input(
                label=label,
                value=default if default is not None else "",
                key=key
            )
        if ptype == list:
            widget = st.text_area(
                label=label,
                value=default if default is not None else "",
                key=key
            )
        if ptype == int:
            widget = st.number_input(
                label=label,
                value=default if default is not None else 0,
                key=key
            )
            widget = int(widget)
        if ptype == float:
            widget = st.number_input(
                label=label,
                value=default if default is not None else 0.0,
                key=key
            )
            widget = float(widget)
        if ptype == bool:
            widget = st.selectbox(
                label=label,
                options=[True, False],
                index=[True, False].index(default) if default in [True, False] else 0,
                key=key
            )
        if ptype == type(None):
            st.write('WARNING: default is None and no type annotation, using text_input')
            widget = st.text_input(label=label, key=key)
        if ptype == os.PathLike:
            if default is not None and os.path.exists(default):
                session_key = f'{key}_input_path'
                ss[session_key] = default
                
            else:
                session_key = f'{key}_input_path'
                ss[session_key] = 'configs'
            ss[session_key] = st_file_selector(label=label, path=ss[session_key],
                                                  st_placeholder=st.empty(), key=key)
            st.write(f"Selected: {ss[session_key]}")
            widget = ss[session_key]
    return widget


def parseobject(obj, exceptions=[]):
    """
    Parse an object (class or function) to identify parameters and annotation including docstring (must be reST/PyCharm style).
    Additionally any list enclosed in square brackets will be interpretted as options. 
    :param obj: The class or function to be parsed
    :param exceptions: A list of parameters to exclude in parsing [example1, example2]
    :return: Object, A dictionary of parameters including name, type, default, description and options
    """
    exceptions += exceptions + ['kwargs']

    # Find type of object
    if inspect.isclass(obj):
        docs = inspect.getdoc(obj.__init__)
    else:
        docs = inspect.getdoc(obj)

    # Remove description
    docs = docs.strip().replace("\n", "").split(":")
    obj_description = docs.pop(0)

    # Inspect parameter info
    sig = inspect.signature(obj).parameters
    params = {}
    for p in sig:
        if p in exceptions:
            continue
        params[p] = {
            'name': p,
            'type': sig[p].annotation if sig[p].annotation != inspect._empty else None,
            'default': sig[p].default if sig[p].default != inspect._empty else None,
            'description': None,
            'options': None
            }
    
    # Add docstring annotation for parameters
    for d in range(0, len(docs), 2):
        if docs[d].split(" ")[0] != 'param':
            continue
        p = docs[d].split(" ")[1]
        if p in exceptions:
            continue
        
        p_description = docs[d+1].strip()
        p_options = re.search("\[(.*?)\]", docs[d+1].strip())
        if p_options is not None:
            p_description = p_description.replace(p_options.group(), "").strip()
            p_options = p_options.group().strip('[]').split(", ")

        try:
            params[p]['description'] = p_description
            params[p]['options'] = p_options
        except KeyError as e:
            print(f'Parameter-docstring mismatch: {e}')
            pass

    return obj, params


def object2dictionary(obj, key_i=0, exceptions=[]):
    """
    Take an object (function or class.__init__) and use the st interface to return
     a dictionary of parameters and arguments - depends on correctly annotated format.
    :param obj: Class or function
    :param key_i: Key identifier
    :param exceptions: Values we don't want user input for
    :return: dict
    """
    result_dict = {}
    obj, params = parseobject(obj, exceptions)

    for p, pinfo in params.items():
        label = f"{p}: {pinfo['description']}"

        # No default
        if pinfo['default'] is None:
            # If no type either, print warning and use text input
            if pinfo['type'] is None:
                st.write(f'WARNING: {p} is has no default or type annotation, using text_input')
                result_dict[p] = st.text_input(label=label, key=f'{key_i}: {obj.__name__}_{p}')
        
            else:
                # Check to see if ptype is union i.e., multiple types possible
                ptype_args = getattr(pinfo['type'], '__args__', None)
                if ptype_args is not None:
                    pinfo['type'] = st.selectbox(label=f'{p}: input type', options=ptype_args,
                                                 index=0, key=f'{key_i}: {obj.__name__}_{p}_type')
                result_dict[p] = type2widget(pinfo['type'], key=f'{key_i}: {obj.__name__}_{p}', label=label, options=pinfo['options'])
                if pinfo['type'] == int: result_dict[p] = int(result_dict[p])

        else:
            # Use type annotation if present
            if pinfo['type'] is not None:
                with st.expander(f"{p}={pinfo['default']}"):
                    # Check to see if ptype is union i.e., multiple types possible
                    ptype_args = getattr(pinfo['type'], '__args__', None)
                    if ptype_args is not None:
                        pinfo['type'] = st.selectbox(label=f'{p}: input type', options=ptype_args,
                                            index=0, key=f'{key_i}: {obj.__name__}_{p}')
                    result_dict[p] = type2widget(pinfo['type'], key=f'{key_i}: {obj.__name__}_{p}',
                                                 default=pinfo['default'], label=label, options=pinfo['options'])
                    #if pinfo['type'] == int: result_dict[p] = int(result_dict[p])

            # Otherwise use type of default
            else:
                with st.expander(f"{p}={pinfo['default']}"):
                    result_dict[p] = type2widget(type(pinfo['default']), key=f'{key_i}: {obj.__name__}_{p}', 
                                                 default=pinfo['default'], label=label, options=pinfo['options'])

        # If list convert correctly
        if pinfo['type'] == list:
            result_dict[p] = result_dict[p].replace(',', '').replace('\n', ' ').split(' ')
            # Check if empty and handle properly
            if result_dict[p] == [''] or result_dict[p] == ['[]'] or result_dict[p] == ['', '']:
                result_dict[p] = []

    return result_dict


def getsfconfig(key_i, tab):
    """
    Get configs for scoring functions
    :param key_i: Key identifier for widgets
    :return: dict
    """
    sf_config = {}
    # Do it in the tab
    with tab:
        # Choose scoring functions
        sf_config['name'] = st.selectbox(
            label='Type',
            options=[s.__name__ for s in scoring_functions.all_scoring_functions if not (s.__name__ in ['TanimotoSimilarity', 'RDKitDescriptors'])], # Remove these as only present for backwards compatability
            index=0,
            key=f'{key_i}: sf_name')
        sf_config['run'] = True
        # Get (class/function) from name ...
        sf_obj = [s for s in scoring_functions.all_scoring_functions if s.__name__ == sf_config['name']][0]
        # Write doc of class (not instance)
        if (sf_config['name'] == 'PIDGIN') and not ss.pidgin_docstring: 
            st.write('Populating options, please wait a minute or two ...')
            sf_obj.set_docstring() # Populate PIDGIN docstring which takes a few seconds
            ss.pidgin_docstring=True
        sf_doc = inspect.getdoc(sf_obj)
        st.markdown('**Description**')
        if sf_doc is not None:
            st.write(sf_doc)
        else:
            st.write('No documentation')
        st.markdown('**Parameters**')
        sf_config['parameters'] = object2dictionary(sf_obj, key_i=key_i)
        st.markdown('**Config format**')
        with st.expander(label='Check parsing'):
            st.write(sf_config)
    return sf_config


def getspconfig(options, key_i, tab):
    """
    Get configs for scoring parameters
    :param options: List of options taken from selected scoring functions
    :param key_i: Key identifier
    :return: dict
    """
    # TODO undo col and change parameters for range/min/max to only those available
    global ss
    sp_config = {}
    # Do it within a tab
    with tab:
        sp_config['name'] = st.selectbox(label='Ouput name',
                                        options=options,
                                        index=0,
                                        key=f'{key_i}: sp_name')
        if sp_config['name'] is None:
            return
        with st.expander(label='Weight (only applicable if using wsum or wprod)'):
            sp_config['weight'] = st.number_input(
                label='weight', value=1.0, key=f'{key_i}: sp_weight'
                )
        # Get (class/function) for transformation/modification from name and print doc ...
        sp_config['modifier'] = st.selectbox(label='Modifier',
                                            options=[m.__name__ for m in utils.all_score_modifiers],
                                            index=0,
                                            key=f'{key_i}: sp_modifier')
        smod_obj = [m for m in utils.all_score_modifiers if m.__name__ == sp_config['modifier']][0]
        # Write doc for func
        smod_doc = inspect.getdoc(smod_obj).split(':')[0]
        st.markdown('**Description**')
        if smod_doc is not None:
            st.write(smod_doc)
        else:
            st.write('No documentation')

        # If norm, optional specification of max/min
        st.markdown('**Parameters**')
        if smod_obj.__name__ == 'norm':
            col1, col2 = st.columns(2)
            # Buttons
            if col1.button(label='Specify max/min', key=f'{key_i}: maxmin') or ss.maxmin:
                ss.maxmin = True
            if col2.button(label='Don\'t specify max/min', key=f'{key_i}: nomaxmin') or not ss.maxmin:
                ss.maxmin = False
            # Grab parameters and plot
            if ss.maxmin:
                sp_config['parameters'] = object2dictionary(smod_obj, key_i=key_i, exceptions=['x'])
            else:
                sp_config['parameters'] = object2dictionary(smod_obj, key_i=key_i, exceptions=['x', 'max', 'min'])

        # Otherwise just do it
        else:
            sp_config['parameters'] = object2dictionary(smod_obj, key_i=key_i, exceptions=['x'])

        col1, col2, col3 = st.columns([1, 1, 1])
        try:
            with col1:
                st.write('Example')
            with col2:
                st.write(utils.transformation_functions.plot_mod(smod_obj, sp_config['parameters']))
        except:
            pass

        st.markdown('**Config format**')
        with st.expander(label='Check parsing'):
            st.write(sp_config)
    return sp_config


# ----- Start App -----
st.title('MolScore Configuration Writer')
config = dict()


# ------ Basic information ------
st.markdown('#') # Add spacing
st.subheader('Run parameters')
config['task'] = st.text_input(label='Task name (for file naming)', value='QED').strip().replace(' ', '_')

config['output_dir'] = st.text_input(label='Output directory', value='./')
absolute_output_path = st.checkbox(label='Absolute path')
if absolute_output_path:
    config['output_dir'] = os.path.abspath(config['output_dir'])
    st.write(f"Selected: {config['output_dir']}")

config['load_from_previous'] = st.checkbox(label='Continue from previous directory')
if config['load_from_previous']:
    col1, col2 = st.columns([1, 9])
    with col2:
        ss.previous_dir = 'configs'
        ss.previous_dir = st_file_selector(label='Select a previously used folder',
                                           st_placeholder=st.empty(),
                                           path=ss.previous_dir,
                                           key='previous_dir_selector')
        config['previous_dir'] = ss.previous_dir
        st.write(f"Selected: {config['previous_dir']}")

# ------ Logging ------
config['logging'] = st.checkbox(label='Verbose logging')

# ------ App monitor ------
config['monitor_app'] = st.checkbox(label='Run live monitor app')

# ----- Diversity filters -----
st.markdown('#') # Add spacing
st.subheader('Diversity filter')
config['diversity_filter'] = {}
config['diversity_filter']['run'] = st.checkbox(label='Run diversity filter')
if config['diversity_filter']['run']:
    config['diversity_filter']['name'] = st.radio(label='Type of filter',
                                                  options=['Unique', 'Occurrence'] +
                                                          [s.__name__ for s in scaffold_memory.all_scaffold_filters],
                                                  index=0)
    if config['diversity_filter']['name'] == 'Unique':
        st.markdown('**Description**')
        st.write('Penalize non-unique molecules by assigning a score of 0')
        st.markdown('**Parameters**')
        config['diversity_filter']['parameters'] = {}
    elif config['diversity_filter']['name'] == 'Occurrence':
        st.markdown('**Description**')
        st.write('Penalize non-unique molecules based on the number of occurrences')
        st.markdown('**Parameters**')
        config['diversity_filter']['parameters'] = {'tolerance': st.number_input(label='Number of duplicates allowed'
                                                                                       ' before penalization',
                                                                                 min_value=0, value=5),
                                                    'buffer': st.number_input(label='Number of linear penalization\'s'
                                                                                    ' until a reward of 0 is returned',
                                                                              min_value=0, value=5)}
    else:  # 'Memory-assisted' types:
        st.markdown('**Description**')
        st.write('Use as dynamic memory: see https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-00473-0')
        # Get (class/function) from name ...
        dv_obj = [s
                  for s in scaffold_memory.all_scaffold_filters
                  if s.__name__ == config['diversity_filter']['name']][0]
        st.markdown('**Parameters**')
        config['diversity_filter']['parameters'] = object2dictionary(dv_obj)
    
    st.markdown('**Config format**')
    with st.expander(label='Check parsing'):
        st.write(config['diversity_filter'])

# ----- Scoring functions ------
st.markdown('#') # Add spacing
st.subheader('Scoring functions')
# Buttons to add and delete scoring function (i.e. append no. of scoring functions to Session State)
col1, col2 = st.columns(2)
with col1:
    if st.button(label='Add scoring function'):
        ss.n_sf += 1
with col2:
    if st.button(label='Delete scoring function'):
        ss.n_sf -= 1
sf_tabs = st.tabs([f"SF{i+1}" for i in range(ss.n_sf)])
# Get user input parameters
config['scoring_functions'] = [getsfconfig(i, tab=t) for i, t in zip(range(ss.n_sf), sf_tabs)]


# ----- Scoring transformations -----
st.markdown('#') # Add spacing
st.subheader('Score transformation')
config['scoring'] = {}

# Buttons to add and delete scoring function (i.e. append no. of scoring functions to Session State)
col1, col2 = st.columns(2)
with col1:
    if st.button(label='Add scoring parameter'):
        ss.n_sp += 1
with col2:
    if st.button(label='Delete scoring parameter'):
        ss.n_sp -= 1
sp_tabs = st.tabs([f"SF{i+1}" for i in range(ss.n_sp)])
# Get user input parameters if scoring functions have been defined
if len(config['scoring_functions']) > 0:
    smetric_options = []
    for sf in config['scoring_functions']:
        sf_name = sf['name']
        sf_prefix = sf['parameters']['prefix']
        sf_obj = [sf for sf in scoring_functions.all_scoring_functions if sf.__name__ == sf_name][0]
        try:
            sf_metrics = sf_obj.return_metrics
            _ = [smetric_options.append(f"{sf_prefix.strip().replace(' ', '_')}_{m}")
                 for m in sf_metrics]
        except AttributeError:
            st.write(f'WARNING: No return metrics found for {sf_name}')
            continue
    # Get parameter inputs
    config['scoring']['metrics'] = [getspconfig(options=smetric_options, key_i=i, tab=t) for i, t in zip(range(ss.n_sp), sp_tabs)]

# ----- Score aggregation -----
st.markdown('#') # Add spacing
st.subheader('Score aggregation')
config['scoring']['method'] = st.radio(
    label='Method',
    options=[m.__name__ for m in utils.all_score_methods],
    index=0,
    key='Scoring method')

# Get (class/function) from name and print doc ...
sm_obj = [s for s in utils.all_score_methods if s.__name__ == config['scoring']['method']][0]
sm_doc = inspect.getdoc(sm_obj)
st.markdown('**Description**')
if sm_doc is not None:
    st.write(sm_doc.split(':')[0])
else:
    st.write('No documentation')


# ----- Output -----
st.markdown('#') # Add spacing
st.subheader('Output json')
with st.expander(label='Show'):
    st.write(config)
out_file = os.path.abspath(st.text_input(label='Output file', value=f'configs/{config["task"]}.json'))
st.write(f"Selected: {out_file}")
col1, col2 = st.columns(2)
with col1:
    if st.button(label='Save'):
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
            st.write('Creating directory')
        with open(out_file, 'w') as f:
            json.dump(config, f, indent=2)
            st.write('File saved')
with col2:
    if st.button(label='Exit'):
        os._exit(0)

# ----- Navigation Sidebar -----
st.sidebar.header('Navigate')
st.sidebar.markdown("[Run parameters](#run-parameters)")
st.sidebar.markdown("[Diversity filter](#diversity-filter)")
st.sidebar.markdown("[Scoring functions](#scoring-functions)")
st.sidebar.markdown("[Score transformation](#score-transformation)")
st.sidebar.markdown("[Score aggregation](#score-aggregation)")
st.sidebar.markdown("[Output](#output-json)")