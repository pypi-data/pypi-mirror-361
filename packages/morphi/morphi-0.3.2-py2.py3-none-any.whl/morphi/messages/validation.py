import subprocess
import sys
import tomli
from pathlib import Path
from .frontend import CompileJson


def read_pyproject_config(root_path):
    pyproject_path = root_path / 'pyproject.toml'
    if not pyproject_path.exists():
        raise FileNotFoundError(f"Could not find pyproject.toml in {root_path}")

    with open(pyproject_path, 'rb') as f:
        config = tomli.load(f)

    babel_config = config.get('tool', {}).get('babel', {})
    if not babel_config:
        raise ValueError("No [tool.babel] configuration found in pyproject.toml")

    return babel_config


def compile_json_catalog(babel_config, locale, domain):
    """Use CompileJson to compile the catalog to JSON format"""
    json_config = babel_config.get('compile_json', {})
    if not json_config:
        return

    cmd = CompileJson()
    cmd.initialize_options()

    # Set options from config
    cmd.directory = json_config.get('directory')
    cmd.output_dir = json_config.get('output_dir')
    cmd.domain = domain
    cmd.locale = locale
    cmd.use_fuzzy = json_config.get('use_fuzzy', False)

    # Finalize and run
    cmd.finalize_options()
    cmd.run()


def check_translations(
    root_path,
    package_name,
    locales=frozenset(['es']),
    ignored_strings=frozenset(),
):
    root_path = Path(root_path)
    setup_py = root_path / 'setup.py'
    i18n_dir = root_path / package_name / 'i18n'
    domain = package_name

    if setup_py.exists():
        # Use existing setup.py approach
        subprocess.run(['python', str(setup_py), 'extract_messages'])
        subprocess.run(['python', str(setup_py), 'update_catalog', '--no-fuzzy-matching'])
        subprocess.run(['python', str(setup_py), 'compile_catalog'])
        subprocess.run(['python', str(setup_py), 'compile_json'])
    else:
        # Use configuration from pyproject.toml
        babel_config = read_pyproject_config(root_path)

        # Extract messages configuration
        extract_config = babel_config.get('extract_messages', {})
        mapping_file = Path(extract_config.get('mapping_file', f'{package_name}/i18n/babel.cfg'))
        output_file = Path(extract_config.get('output_file', f'{package_name}/i18n/{package_name}.pot'))
        input_dirs = extract_config.get('input_dirs', [package_name])

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Extract messages
        subprocess.run([
            'pybabel', 'extract',
            '-F', str(mapping_file),
            '-o', str(output_file),
            *input_dirs
        ], check=True)

        # Get common configuration
        domain = babel_config.get('init_catalog', {}).get('domain', package_name)
        i18n_dir = Path(babel_config.get('compile_catalog', {}).get('directory', f'{package_name}/i18n'))

        # Process each locale
        for locale in locales:
            po_dir = i18n_dir / locale / 'LC_MESSAGES'
            po_file = po_dir / f'{domain}.po'

            if not po_dir.exists():
                po_dir.mkdir(parents=True)
                # Initialize catalog if it doesn't exist
                subprocess.run([
                    'pybabel', 'init',
                    '-i', str(output_file),
                    '-d', str(i18n_dir),
                    '-l', locale,
                    '-D', domain
                ], check=True)
            else:
                # Update existing catalog
                subprocess.run([
                    'pybabel', 'update',
                    '-i', str(output_file),
                    '-d', str(i18n_dir),
                    '-l', locale,
                    '-D', domain,
                    '--no-fuzzy-matching'
                ], check=True)

            # Compile catalog
            use_fuzzy = babel_config.get('compile_catalog', {}).get('use_fuzzy', False)
            compile_cmd = [
                'pybabel', 'compile',
                '-d', str(i18n_dir),
                '-l', locale,
                '-D', domain,
            ]
            if use_fuzzy:
                compile_cmd.append('--use-fuzzy')
            subprocess.run(compile_cmd, check=True)

            # Compile JSON using morphi's CompileJson
            compile_json_catalog(babel_config, locale, domain)

    # Validation logic
    found_fuzzy = False
    untranslated_strings = []

    for locale in locales:
        po_path = i18n_dir / locale / 'LC_MESSAGES' / f'{domain}.po'
        with open(po_path, mode='rb') as fp:
            contents = fp.read()
            found_fuzzy = found_fuzzy or b'#, fuzzy' in contents

            fp.seek(0)
            from babel.messages.pofile import read_po
            load_catalog = read_po(fp)
            for message in load_catalog:
                if message.id in ignored_strings:
                    continue
                if message.id and not message.string:
                    untranslated_strings.append(f'{locale}: {message.id}')

    if found_fuzzy:
        print('Detected fuzzy translations.')

    if untranslated_strings:
        print('Did not find translations for the following strings:')
        for item in untranslated_strings:
            print('    ', item)

    if found_fuzzy or untranslated_strings:
        print('Edit the PO file and compile the catalogs.')
        sys.exit(1)

    print('No detected translation issues.')
