import os
import logging
import argparse
import subprocess


logger = logging.getLogger("smiet.make_docs")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog="smiet.docs.make_docs",
        description=(
            "A script to automatically generate the API documentation for template synthesis,"
            " and build the html documentation for online publishing."
        )
    )
    argparser.add_argument(
        '--no-clean', default=False, const=True, action='store_const',
        help=(
            "Do not delete existing html files and build only pages which have changed."
            " Useful if you are only modifying or adding (not moving/removing) pages.")
    )
    argparser.add_argument(
        '--skip-apidoc', default=False, const=True, action='store_const', help=(
            "Skip the compilation of the automatic API documentation. "
            "Speeds up the compilation of the documentation if no changes were made to the code.")
    )
    parsed_args = argparser.parse_args()

    # create the automatic code documentation with apidoc
    output_folder = 'source/apidoc'
    if os.path.exists(output_folder):
        if not parsed_args.no_clean: # remove old apidoc folder
            logger.info('Removing old apidoc folder: {}'.format(output_folder))
            subprocess.check_output(['rm', '-rf', output_folder])


    module_path = '../smiet/'
    subprocess.run(
        [
            'sphinx-apidoc', '-efMT', '-d', '1', '--ext-autodoc', '--ext-intersphinx',
            '--ext-coverage', '--ext-githubpages', '-o', output_folder,
            module_path
        ]
    )

    # We don't use the top level APIDOC toctrees, so we remove them to eliminate a sphinx warning
    subprocess.check_output([
        'rm',
        os.path.join(output_folder, 'smiet.numpy.rst'),
        os.path.join(output_folder, 'smiet.jax.rst'),
        os.path.join(output_folder, 'smiet.rst')
    ])

    if os.path.exists('build'):
        subprocess.check_output(['rm', '-rf', 'build'])
    subprocess.run(
            ['sphinx-build', '-M', 'html', 'source', 'build'],
        )
