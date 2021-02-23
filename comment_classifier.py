import glob
import json
from tqdm import tqdm
import os
from collections import Counter
import argparse
import sys
import re

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", type=str)
parser.add_argument("--output_dir", type=str)

class Classifier:
    special_neutral_words = ['will call', 'will follow', 'will inform']
    good_words = ['settle', 'settled', 'settlled', 'no margin', 'sold', 'selling',
              'no call', 'deposite', 'deposit', 'promise', 'dividend recievable', 'dividend receivable',
              'approved', 'conversion', 'buy back', 'transfer', 'release cash', 'covered', 'sell', 
              'no margin', 'refund', 'fx', 'excess status', 'return', 'not under margin call', 'liquidate',
              'made&already']
    neutral_words = ['extent', 'special', 'contacted', 'sent', 'email client', 'called', 'notified', 'obtained',
                    'force sell', '1)', 'extend', 'voice message', 'inform', 'extension', 'emailed', 'locked',
                     'have enough purchasing power', 'have enough power', 'has enough purchasing power', 'has enough power',
                     'email', 'defer']
    ext_neutral_words = ['via', 'ex', 'ext']
    bad_words = ["can't reach", "can' t reach", 'cannot reach', 'out of town', 'will back to hong', 
                 'unreachable', 'cant reach']

    def __init__(self, input_file_dir, output_file_dir):
        all_json_paths = glob.glob(input_file_dir + '/*.json')
        self.output_file_dir = output_file_dir
        try:
            os.makedirs(output_file_dir, exist_ok=True)
        except:
            print('failed to create output_dir, app exit')
            sys.exit()
        self.emails = []
        self.input_json_paths = []
        self.failed_paths = []
        print(f'reading email data from {input_file_dir}')
        for path in all_json_paths:
            try:
                with open(path) as f:
                    email = json.load(f, strict=False)
                if 'Others (Optional)' in email:
                    self.emails.append(email)
                    self.input_json_paths.append(path)
                else:
                    self.failed_paths.append(path)
            except Exception as e:
                self.failed_paths.append(path)
        print(f'the following emails cannot be read:\n{self.failed_paths}')
        print(f'{len(self.emails)} emails read successfully')

    def _input_to_output(self):
        for i in range(len(self.emails)):
            email = self.emails[i]

            comment = email['Others (Optional)'].lower()
            result = 'Unkown'
        
            if comment == '': 
                result = 'Empty'

            if result == 'Unkown':
                for word in self.special_neutral_words:
                    if word in comment:
                        result = 'Neutral'
                        break

            if result == 'Unkown':
                for word in self.good_words:
                    if word in comment:
                        result = 'Good'
                        break
            
            if result == 'Unkown':
                for word in self.bad_words:
                    if word in comment:
                        result = 'Bad'
                        break
            
            if result == 'Unkown':
                for word in self.neutral_words:
                    if word in comment:
                        result = 'Neutral'
                        break

            if result == 'Unkown':
                for word in self.ext_neutral_words:
                    if word in comment:
                        if len(re.findall(r"\D(\d{5})\D", comment)) > 0:
                            result == 'Neutral'
                            break

            
            self.emails[i]['NLP Analysis Result'] = result

    def _save_output_emails(self):
        print(f'writing output json to {self.output_file_dir}')
        failed_writing_emails = []
        for i in range(len(self.emails)):
            try:
                email = self.emails[i]
                input_path = self.input_json_paths[i].replace('\\', '/')
                input_file_name = input_path.split('/')[-1].split('.')[0]
                output_path = self.output_file_dir + '/' + input_file_name + '_processed.json'
                with open(output_path, 'w') as f:
                    json.dump(email, f)
            except Exception as e:
                failed_writing_emails.append(input_file_name)
        print(f'the following emails cannot be written: {failed_writing_emails}')
    
    def run(self):
        self._input_to_output()
        self._save_output_emails()
        print('done!')

if __name__ == '__main__':
    args = parser.parse_args()
    input_dir = args.input_dir.replace('\\', '/')
    output_dir = args.output_dir.replace('\\', '/')
    classifier = Classifier(input_dir, output_dir)
    classifier.run()