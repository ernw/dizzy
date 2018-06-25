#       setup.py
#
#       Copyright 2017 Daniel Mende <mail@c0decafe.de>
#

#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the  nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from setuptools import setup
from dizzy.config import CONFIG

setup(name='dizzy',
      version=CONFIG["GLOBALS"]["VERSION"],
      description='Dizzy Fuzzing Library',
      author='Daniel Mende',
      author_email='mail@c0decafe.de',
      url='https://c0decafe.de',
      license='BSD',
      classifiers=[ 'Development Status :: 4 - Beta',
                    'Environment :: Console',
                    'License :: OSI Approved :: BSD License',
                    'Natural Language :: English ',
                    'Operating System :: POSIX',
                    'Operating System :: Microsoft :: Windows',
                    'Programming Language :: Python :: 3 :: Only',
                    'Topic :: Security',
                    'Topic :: Software Development :: Testing'],
      packages=['dizzy', 'dizzy.encodings', 'dizzy.functions', 'dizzy.objects', 'dizzy.probe', 'dizzy.session'],
      scripts=['dizzy_cmd'],
      data_files=[('share/dizzy/', ['lib/std_string_lib.txt'])],
      python_requires='>=3',
      install_requires=[
          'exrex',
      #    'Crypto'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      )
