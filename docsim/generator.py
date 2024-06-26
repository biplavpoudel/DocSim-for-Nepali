import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from tqdm import tqdm
from docsim.utils.random import random_id
from docsim.text_generators import *
from docsim.image_generators import *
import random
from faker import Faker

class Generator:
    def __init__(self, template_json):
        
        if type(template_json) == dict:
            template = template_json
        else:
            with open(template_json, encoding='utf-8') as f:
                template = json.load(f)
        self.metadata = []
        self.doc_name = template['doc_name']
        self.bg_img = template['background_img']
        self.DEBUG = template['debug_mode'] if 'debug_mode' in template else False
    
        self.set_defaults(template)
        self.setup_components(template)
        self.setup_static_components(template)
    
    def set_defaults(self, template):
        '''
        Set default configurations for the given template
        '''
        self.default_config = template['defaults']
        
        self.DEFAULT_VALUES = {
            'font_color': 'rgb(0,0,0)',
            'font_size': 12,
            
            'lang': 'en',
            
            # Post-Processing
            'multiline': True, # Allow multi-line rendering
            'split_words': False,
            'upper_case': False, # Do Not Force Upper-casing
            
            # Metadata
            'entity': None, # Entity-type. e.g.: Name, Date, Gender, etc.
            'already_printed': False, # Marks if the component is already printed (static)
        }
        
        # Set global default configs for template
        for key, value in self.DEFAULT_VALUES.items():
            if key not in self.default_config:
                self.default_config[key] = value
        
        if 'font_files' not in self.default_config:
            self.default_config['font_files'] = {'en': None}
        # self.default_fonts = {lang: ImageFont.truetype(self.default_config['font_files'][lang], size=self.default_config['font_size']) for lang in self.default_config['font_files']}
        
        self.default_config['post_processor'] = TextPostProcessor(upper_case=self.default_config['upper_case'],
                                                                  multiline=self.default_config['multiline'])
        
        return
         
    def setup_components(self, template):
        '''
        Assign generators to each component in the template
        '''
        self.components = template['components']
        for component_name, component in self.components.items():
            
            component['id'] = component_name
            if 'filler_source' in component:
                component['data_source'] = self.components[component['filler_source']]
            
            # Setup component-specific config from defaults
            for config_key in self.DEFAULT_VALUES:
                if config_key not in component:
                    component[config_key] = self.default_config[config_key]
            
            if component['type'] == 'text':
                
                # Setup font based on language
                if 'font_file' not in component:
                    component['font_file'] = self.default_config['font_files'][component['lang']]
                component['font'] = ImageFont.truetype(component['font_file'], size=component['font_size'])
                
                # Setup the generator using filling method                
                if component['filler_mode'] == 'random':
                    if component['filler_type'] == 'full_name':
                        component['generator'] = FullNameGenerator(component['lang'])
                    elif component['filler_type'] == 'multiline_full_name':
                        component['generator'] = MultilineFullNameGenerator(component['lang'])
                    elif component['filler_type'] == 'account_full_name':
                        component['generator'] = AccNameGenerator(component['lang'])
                    elif component['filler_type'] == 'amount_nepali':
                        component['generator'] = NepaliCurrencyGenerator()
                    elif component['filler_type'] == 'child_name':
                        component['generator'] = ChildNameFromParentGenerator(component['lang'], component['data_source'])
                    elif component['filler_type'] == 'address':
                        component['generator'] = AddressGenerator(
                            language = component['lang'], type = component['address_type'])
                    else:
                        raise NotImplementedError
                elif component['filler_mode'] == 'regex':
                    component['generator'] = TextFromRegexGenerator(component['filler_regex'])
                elif component['filler_mode'] == 'array':
                    component['generator'] = TextFromArrayGenerator(component['filler_options'])
                elif component['filler_mode'] == 'fixed':
                    component['generator'] = TextFromArrayGenerator([component['filler_text']])
                elif component['filler_mode'] == 'unicode':
                    component['generator'] = UnicodeGenerator([component['unicode']])
                elif component['filler_mode'] == 'reference':
                    component['generator'] = ReferentialTextGenerator(component['data_source'])
                elif component['filler_mode'] == 'transliteration':
                    component['generator'] = ReferentialTextTransliterator(component['data_source']['lang'], component['lang'], component['data_source'])
                else:
                    raise NotImplementedError
                
                # Setup post-processing. TODO: Optimize? (Too many same objects)
                component['post_processor'] = TextPostProcessor(upper_case=component['upper_case'], multiline=component['multiline'])
            
            elif component['type'] == 'image':
                if component['filler_mode'] == 'random':
                    component['generator'] = ImageGenerator(component['image_folder'], component['dims'])
                elif component['filler_mode'] == 'static':
                    component['generator'] = ImageRetriever(component['image_file'], component['dims'])
                elif component['filler_mode'] == 'random_face_online':
                    component['generator'] = OnlineFaceGenerator(component['dims'])
                elif component['filler_mode'] == 'qr':
                    component['generator'] = QRCodeGenerator(component)
                elif component['filler_mode'] == 'barcode':
                    component['generator'] = BarCodeGenerator(component)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        
        return
    
    def setup_static_components(self, template):
        '''
        We draw bboxes for already printed static text. So set it up
        '''
        if 'printed_fields' not in template:
            return
    
        for component_name, component in template['printed_fields'].items():
            if component_name in self.components:
                exit('Component name %s already taken' % component_name)
            component['id'], component['already_printed'] = component_name, True
            
            if component['type'] == 'text':
                # TODO: Set using DEFAULT_VALUES
                if 'lang' not in component:
                    component['lang'] = self.default_config['lang']
                if 'split_words' not in component:
                    component['split_words'] = False #self.default_config['split_words']
                if 'entity' not in component:
                    component['entity'] = None
            
            self.components[component_name] = component
    
        return
    
    def generate_sample(self, output_folder):
        '''
        Generate a random sample and save it
        '''
        image = Image.open(self.bg_img)
        img_draw = ImageDraw.Draw(image)
        ground_truth = []
        ground_truth_donut = []

        # for Global Nepali cheque only
        y_check_offset = [0, -17]
        y_check_variable = random.choice(y_check_offset)

        for component_name, component in self.components.items():
            if component['type'] == 'text':
                # To know if draw_text() or draw_words() is invoked
                # print(component['split_words'],"for entity:", component['entity'])
                if component['split_words']:
                    metadata = self.draw_words(img_draw, component)
                else:
                    metadata = [self.draw_text(img_draw, component, check_variable = y_check_variable)]
                ground_truth.extend(metadata)
            elif component['type'] == 'image':
                metadata = self.draw_img(image, component)
                ground_truth.append(metadata)
            else:
                raise NotImplementedError

        filename = random_id()
        output_file = os.path.join(output_folder, filename)

        # Creating an equivalent ground truth for DONUT Transformer
        '''
         {"file_name": "118.jpg",
         "ground_truth": "{\"gt_parse\":
         {\"cheque_details\":[
            {\"date\": \"19042024\",
            \"payee\": \"Bhukampa prabhabit rahat kosh Jajarkot 2080\",
            \"sum\": \"One lakh Only\",
            \"amount\": \"100000/-\",
            \"account_number\": \"B501010000152\",
            \"account_name\": \"NEPAL CAMPUS CRUSADE FOR CHRIST\",
            \"micr\": 49423485.0,
            \"A/C_Payee\": \"A/C PAYEE ONLY\"}
            ]}}"}
        '''

        file_name = filename + ".jpg"
        payee = ground_truth[1]["text"].replace("\n","")
        sums = ground_truth[2]["text"].replace("  "," ")
        amount = ground_truth[3]["text"].replace("\n","")
        date = ground_truth[0]["text"].replace(" ","").replace("\n","")

        # print("File name: ",file_name,"\nDate: ",date, "\nPayee: ",payee, "\nSums: ",sums,"\nAmount: ", amount)

        gt_parse = {
            "cheque_details": {
                'date': date,
                'payee': payee,
                'sum': sums,
                'amount': amount
            }
        }

        gt = {
            'file_name': file_name,
            'ground_truth': json.dumps({'gt_parse': gt_parse}, ensure_ascii=False)
        }

        self.metadata.append(gt)

        image.save(output_file+'.jpg')
        # with open(output_file+'.json', 'w', encoding='utf-8') as f:
        #     json.dump(gt, f, ensure_ascii=False, indent=4)
        
        return output_file
    
    def generate(self, num_samples, output_folder=None):
        '''
        Bulk generate samples
        '''
        if not output_folder:
            output_folder = os.path.join('output', self.doc_name)
        os.makedirs(output_folder, exist_ok=True)
        output_files = []
        
        for i in tqdm(range(num_samples)):
            output_file = self.generate_sample(output_folder)
            output_files.append(output_file)
        # print(self.metadata)
        self.create_annotation_entity(output_folder)
        return output_files
    
    def draw_text(self, img_draw, component, check_variable):
        '''
        Render text on image for the given component.
        '''
        # For chequebook of Global IME Bank
        if component["entity"] == "cheque_amount_words" or component["entity"] == "cheque_payee_name":
            x, y = component['location']['x_left'], component['location']['y_top'] + check_variable

        # For account opening bank form of Everest Bank
        elif component["entity"] == "account_checkbox":
            x_offset, y_offset = [0, 233, 515], [0, 23, 50]
            x_variable, y_variable = random.choice(x_offset), random.choice(y_offset)
            x, y = component['location']['x_left'] + x_variable, component['location']['y_top'] + y_variable
        elif component["entity"] == "currency_checkbox":
            x_offset = [0, 80]
            x_variable = random.choice(x_offset)
            x, y = component['location']['x_left']+x_variable, component['location']['y_top']
            # If foreign currency is ticked, I need to add a code that writes foreign currency spec and source
            # my brain isn't braining for now, so separate elif statement for now
        elif component["entity"] == "purpose":
            x_variable= random.choice([0, 82, 216, 335, 460])
            x, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        elif component["entity"] == "nominee_check":
            x_variable= random.choice([0, 90])
            x, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        elif component["entity"] == "guardian_check":
            x_variable= random.choice([0, 75, 165])
            x, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        elif component["entity"] == "mode_account_operation":
            coord = random.choice([True, False])
            if coord:
                x_variable, y_variable = random.choice([0, 165]), 0
            else:
                x_variable, y_variable = 0, random.choice([0, 20])
            x, y = component['location']['x_left'] + x_variable, component['location']['y_top'] + y_variable
        # default if no entity matching occurs
        else:
            x, y = component['location']['x_left'], component['location']['y_top']

        # x, y = component['location']['x_left'], component['location']['y_top']
        if component['already_printed']:
            width, height = component['dims']['width'], component['dims']['height']
            text = component['text']
        else:
            align = component["align"] if "align" in component else "left"
            spacing = component["spacing"] if "spacing" in component else 4
            text = component['generator'].generate()
            component['last_generated'] = text
            text = component['post_processor'].process(text)
            img_draw.text((x, y), text, fill=component['font_color'], font=component['font'], align=align, spacing=spacing)
            width, height = img_draw.textsize(text, font=component['font'])
        self.DEBUG and img_draw.rectangle([(x,y), (x+width+1, y+height+1)], outline='rgb(255,0,0)')
        return {
            'type': component['type'],
            'label': component['id'],
            'entity': component['entity'],
            'points': [ # Clock-wise
                [x+1, y+1], # Left Top
                [x+width+1, y+1], # Right Top
                [x+width+1, y+height+1], # Right Bottom
                [x+1, y+height+1] # Left bottom
            ],
            'width': width,
            'height': height,
            'text': text,
            'lang': component['lang']
        }

    def draw_words(self, img_draw, component):
        '''
        Render text with individual words on image for the given component.
        '''

        #starting point of text(top left corner)
        # if component["entity"]=="amount_words" or component['entity']=="name":
        #     variable_height = variable_height
        # else:
        #     variable_height = 0
        if component["entity"] == "account_checkbox":
            x_offset, y_offset = [0, 233, 515], [0, 23, 50]
            x_variable, y_variable = random.choice(x_offset), random.choice(y_offset)
            x_left, y = component['location']['x_left'] + x_variable, component['location']['y_top'] + y_variable
        elif component["entity"] == "currency_checkbox":
            x_offset = [0, 80]
            x_variable = random.choice(x_offset)
            x_left, y = component['location']['x_left']+x_variable, component['location']['y_top']
            # If foreign currency is ticked, I need to add a code that writes foreign currency spec and source
            # my brain isn't braining for now, so separate elif statement for now
        elif component["entity"] == "purpose":
            x_variable= random.choice([0, 82, 216, 335, 460])
            x_left, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        elif component["entity"] == "nominee_check":
            x_variable= random.choice([0, 90])
            x_left, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        elif component["entity"] == "guardian_check":
            x_variable= random.choice([0, 75, 165])
            x_left, y = component['location']['x_left'] + x_variable, component['location']['y_top']
        else:
            x_left, y = component['location']['x_left'], component['location']['y_top']


        bboxes = []
        if component['already_printed']:
            # Draw word-level bboxes for the pre-printed static text
            # How? Calculate width for each word's bbox in given text
            raise NotImplementedError
            # Experimental Implementation:
            width, height = component['dims']['width'], component['dims']['height']
            text = component['text']
            lines = text.split('\n')
            h = height // len(lines)
            # font = ImageFont.truetype(self.default_fonts[component['lang']].path, h)
            # space_width, h = img_draw.textsize(' ', font=font)
            for row_num, line in enumerate(lines):
                x, char_index = x_left, 0
                # Assumes an equal width font for all characters. What else can I do
                unit_width = width / float(line.count(' ')/2 + len(line.replace(' ', '')))
                space_width = int(unit_width/2)
                for col_num, word in enumerate(line.split()):
                    w = int(unit_width * len(word) + 0.99)
                    # w, h = img_draw.textsize(word, font=font)
                    self.DEBUG and img_draw.rectangle([(x,y), (x+w+1, y+h+1)], outline='rgb(255,0,0)')
                    bboxes.append({
                        'type': component['type'],
                        'label': '%s--%d_%d' % (component['id'], row_num, col_num),
                        'entity': component['entity'],
                        'points': [ # Clock-wise
                            [x+1, y+1], # Left Top
                            [x+w+1, y+1], # Right Top
                            [x+w+1, y+h+1], # Right Bottom
                            [x+1, y+h+1] # Left bottom
                        ],
                        'width': w,
                        'height': h,
                        'text': word,
                        'lang': component['lang']
                    })
                    
                    char_index += len(word)
                    x += w
                    while char_index < len(line) and line[char_index] == ' ':
                        x += space_width
                        char_index += 1
                y += height
                x = x_left
            
        else:
            # Split text into words and draw each word separately
            align = component["align"] if "align" in component else "left"
            spacing = component["spacing"] if "spacing" in component else 4
            text = component['generator'].generate()
            # print("generated text is:", text)
            component['last_generated'] = text
            text = component['post_processor'].process(text)
            space_width, height  = img_draw.textsize(' ', font=component['font'])
            for row_num, line in enumerate(text.split('\n')):
                x, char_index = x_left, 0
                for col_num, word in enumerate(line.split()):
                    img_draw.text((x, y), word, fill=component['font_color'], font=component['font'], align=align, spacing=spacing)
                    w, h  = img_draw.textsize(word, font=component['font'])
                    self.DEBUG and img_draw.rectangle([(x,y), (x+w+1, y+h+1)], outline='rgb(255,0,0)')
                    if h > height: # Variable-height fonts
                        height = h
                    bboxes.append({
                        'type': component['type'],
                        'label': '%s--%d_%d' % (component['id'], row_num, col_num),
                        'entity': component['entity'],
                        'points': [ # Clock-wise
                            [x+1, y+1], # Left Top
                            [x+w+1, y+1], # Right Top
                            [x+w+1, y+h+1], # Right Bottom
                            [x+1, y+h+1] # Left bottom
                        ],
                        'width': w,
                        'height': h,
                        'text': word,
                        'lang': component['lang']
                    })
                    
                    char_index += len(word)
                    x += w
                    while char_index < len(line) and line[char_index] == ' ':
                        x += space_width
                        char_index += 1
                
                y += height
                x = x_left
        
        return bboxes
    
    def draw_img(self, background, component):
        '''
        Draw the given image on background for the given component.
        '''
        x, y = component['location']['x_left'], component['location']['y_top']
        width, height = component['dims']['width'], component['dims']['height']
        if not component['already_printed']:
            img, details = component['generator'].generate()
            # Ensure the image has an alpha channel
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background.paste(img, (x, y), img)  # Use the image itself as the mask
            else:
                background.paste(img, (x, y))
            # background.paste(img, (x, y))
        
        return {
            'type': component['type'],
            'label': component['id'],
            'mode': component['filler_mode'],
            'details': details,
            'points': [ # Clock-wise
                [x+1, y+1], # Left Top
                [x+width+1, y+1], # Right Top
                [x+width+1, y+height+1], # Right Bottom
                [x+1, y+height+1] # Left bottom
            ],
            'width': width,
            'height': height,
        }

    def create_annotation_entity(self, output_folder):
        '''
        Create a single metadata.jsonl for all the synthesized images
        '''
        json_name = 'metadata.jsonl'
        output_directory = output_folder

        # Ensure the directory exists
        os.makedirs(output_directory, exist_ok=True)

        # File path with the desired directory
        file_path = os.path.join(output_directory, json_name)

        for labels in self.metadata:
            with open(file_path, 'a', encoding='utf-8') as f:
                # Convert dictionary to a JSON string with Unicode and ASCII encoding
                json_string = json.dumps(labels, ensure_ascii=False)
                f.write(json_string + '\n')