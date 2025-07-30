from setuptools import setup, find_packages

setup(
    name='cam2text',
    version='0.1.1',  # 🔁 Bump version each time you upload
    description='Convert CCTV/video footage into readable activity text logs',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Sarvesh Upasani',
    author_email='upasanisarvesh45@gmail.com',
    url='https://github.com/sarveshprjs/cam2text',
    packages=find_packages(),
    include_package_data=True,  # ✅ Add this
    package_data={              # ✅ And this
        'cam2text': ['models/*.caffemodel', 'models/*.prototxt.txt']
    },
    install_requires=[
        'opencv-python',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
