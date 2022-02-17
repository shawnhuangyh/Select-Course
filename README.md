# Select Course

## Requirements 

- Python3
- Dependencies
  - requests
  - beautifulsoup4
  - lxml
  - rsa

## Usage

1. Install dependencies

``pip3 install -r requirements.txt``

2. Run the code

``python3 main.py``

3. Input your account and password

Follow the instructions to input your account and password.

4. Input term ID

Input your target term. The term number is consists of 5 digits. The first 4 digits represent the year this semester begins. The last digit represents the term number.

For example, the 2021-2022 spring semester should be ``20213``.

5. Input your Course No. and Teacher No.

Follow the insturctions to input the course number and teacher number.

6. Enjoy.

The program will use course query to check the availability of the course. If the course is available, the program will try to select the course.

## Todo

- [x] Refactor the code
- [ ] Support query multiple courses at the same time
- [ ] ...