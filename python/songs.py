from modes import RenderMode
import instruments
import os
from PIL import Image, ImageDraw, ImageFont

class Song():

    def __init__(self):
        
        self.lines = []
        self.title = 'Untitled'
        self.headers = [['Original Artist(s):', 'Transcript:', 'Musical key:'], ['', '', '']]
        self.maxIconsPerLine = 10
        self.maxLinesPerFile = 10
        self.maxFiles = 10
        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (0.1, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps
        
        self.SVG_viewPort = (0.0, 0.0, 1334.0, 750.0)
        minDim = self.SVG_viewPort[2]*0.01
        self.SVG_viewPortMargins = (13.0, 7.5)
        self.pt2px = 96.0/72
        self.fontpt = 12
        self.SVG_text_height = self.fontpt * self.pt2px # In principle this should be in em
        self.SVG_line_width = self.SVG_viewPort[2]-self.SVG_viewPortMargins[0]
        SVG_harp_width =  max(minDim, (self.SVG_viewPort[2] - self.SVG_viewPortMargins[0])/(1.0*self.maxIconsPerLine*(1+self.harp_relspacings[0])))
        self.SVG_harp_size = (SVG_harp_width, max(minDim, SVG_harp_width / self.harp_AspectRatio) )
        self.SVG_harp_spacings = (self.harp_relspacings[0]*SVG_harp_width, self.harp_relspacings[1]*SVG_harp_width/self.harp_AspectRatio)
        
        self.png_size = (750*2, 1334*2) # must be an integer tuple
        self.png_margins = (13, 7)
        self.png_harp_size0 = instruments.Harp().render_in_png().size #A tuple
        self.png_harp_spacings0 = (int(self.harp_relspacings[0]*self.png_harp_size0[0]), int(self.harp_relspacings[1]*self.png_harp_size0[1]))
        self.png_harp_size = None
        self.png_harp_spacings = None
        self.png_line_width = int(self.png_size[0] - self.png_margins[0])
        self.png_lyric_height = instruments.Voice().get_lyric_height()
        self.png_dpi = (96*2, 96*2)
        self.png_compress = 6
        self.png_color = (255, 255, 255)
        self.png_font_size = 24
        self.png_title_font_size = 36
        self.png_font = 'elements/Roboto-Regular.ttf' 
        self.font_color = (0, 0, 0)
 
    def add_line(self, line):
        if len(line)>0:
            if isinstance(line[0], instruments.Instrument):
                self.lines.append(line)
        
    def get_line(self, row):
        try:
            return self.lines[row]
        except:
            return [[]]
        
    def get_instrument(self, row, col):
        try:
            return self.lines[row][col]
        except:
            return []
    
    def get_max_instruments_per_line(self):        
        if len(self.lines) > 0:
            return max(list(map(len, self.lines)))        
    
    def set_title(self, title):
        self.title = title
        
    def set_headers(self, original_artists='', transcript_writer='', musical_key=''):
        self.headers[1] = [original_artists, transcript_writer, musical_key]

    def get_voice_SVG_height(self):
        return self.fontpt*self.pt2px
    
    def set_png_harp_size(self):       
        if self.png_harp_size == None or self.png_harp_spacings == None:
            Nmax = min(self.maxIconsPerLine, self.get_max_instruments_per_line())
            new_harp_width = min(self.png_harp_size0[0], (self.png_size[0]-self.png_margins[0])/(Nmax * (1 + self.harp_relspacings[0])))
            self.png_harp_size = (new_harp_width, new_harp_width/self.harp_AspectRatio)
            self.png_harp_spacings = (self.harp_relspacings[0]*self.png_harp_size[0], self.harp_relspacings[1]*self.png_harp_size[1])
    
    def get_png_harp_rescale(self):
        if self.png_harp_size[0] != None:
            return 1.0*self.png_harp_size[0]/self.png_harp_size0[0]
        else:
            return 1.0
     
    def get_png_text_height(self, fnt):
            return fnt.getsize('HQfgjyp')[1]
    
    def write_html(self, file_path, note_width='1em', embed_css=True, css_path='css/main.css'):
        
        try:
            html_file = open(file_path, 'w+')
        except:
            print('Could not create text file.')
            return '' 
        
        html_file.write('<!DOCTYPE html>'
                        '\n<html xmlns:svg=\"http://www.w3.org/2000/svg\">')
        html_file.write('\n<head>\n<title>' + self.title + '</title>')  
        
        try:
            with open(css_path, 'r') as css_file:
                css_file = css_file.read()
        except:
            print('Could not open CSS file.')
            css_file = ''
    
        if embed_css in [True, 'True']:
            html_file.write('\n<style type=\"text/css\"><![CDATA[\n')
            html_file.write(css_file)
            html_file.write('\n]]></style>')
        elif embed_css in ['IMPORT', 'import']:
            css_path = os.path.relpath(css_path, start=os.path.dirname(file_path)).replace('\\','/')
            html_file.write('\n<style type=\"text/css\">')
            html_file.write("@import url(\'" + css_path + "\');</style>") 
        elif embed_css in ['XML', 'xml', 'href', 'HREF', False, 'False']:
            css_path = os.path.relpath(css_path, start=os.path.dirname(file_path))
            html_file.write('\n<link href=\"' + css_path + '\" rel=\"stylesheet\" />')
            
        html_file.write('\n<meta charset="utf-8"/></head>\n<body>')
        html_file.write('\n<h1> ' + self.title + ' </h1>')
      
        for i in range(len(self.headers[0])):
            html_file.write('\n<p> <b>' + self.headers[0][i] + '</b> ' + self.headers[1][i] + ' </p>')
    
        html_file.write('\n<div id="transcript">\n')
        
        song_render = ''
        instrument_index = 0
        for line in self.lines:
            if len(line) > 0:
                if line[0].get_type() == 'voice':
                    song_render += '\n<br />'
                else:
                    song_render += '\n<hr />'              
                            
                line_render = '\n'
                for instrument in line:
                    instrument.set_index(instrument_index)
                    instrument_render = instrument.render_in_html(note_width) 
                    instrument_render += ' '
                    instrument_index += 1
                    line_render += instrument_render
    
                song_render += line_render
        
        html_file.write(song_render)
        
        html_file.write('\n</div>'
                        '\n</body>'
                        '\n</html>')
    
        return file_path
    
    
    def write_ascii(self, file_path, render_mode = RenderMode.SKYASCII):    
    
        try:
            ascii_file = open(file_path, 'w+')
        except:
            print('Could not create text file.')
            return ''
        
        ascii_file.write('#' + self.title + '\n')

        for i in range(len(self.headers[0])):
            ascii_file.write('#' + self.headers[0][i] + ' ' + self.headers[1][i])

        song_render = '\n'
        instrument_index = 0
        for line in self.lines:
            line_render = ''
            for instrument in line:
                instrument.set_index(instrument_index)
                instrument_render = instrument.render_in_ascii(render_mode) 
                instrument_index += 1
                line_render += instrument_render
            song_render += '\n' + line_render
                
        ascii_file.write(song_render)
    
        return file_path
    
    def write_svg(self, file_path0, embed_css=True, css_path='css/main.css', start_row=0, filenum=0):    
        
        if filenum>self.maxFiles:
            print('\nYour song is too long. Stopping at ' + str(self.maxFiles) + ' files.')
            return filenum, file_path0

        if filenum>0:
            (file_base, file_ext) = os.path.splitext(file_path0)
            file_path = file_base + str(filenum) + file_ext
        else:
            file_path = file_path0
            
        try:
            svg_file = open(file_path, 'w+')
        except:
            print('Could not create SVG file.')
            return filenum, ''
                
        # SVG/XML headers
        svg_file.write('<?xml version=\"1.0\" encoding=\"utf-8\" ?>')
        
        try:
            with open(css_path, 'r') as css_file:
                css_file = css_file.read()
        except:
            print('Could not open CSS file.')
            css_file = ''
            pass
        
        if embed_css in ['XML', 'xml', 'href', 'HREF', False, 'False']:            
            css_path = os.path.relpath(css_path, start=os.path.dirname(file_path))
            svg_file.write('\n<?xml-stylesheet href=\"' + css_path + '\" type=\"text/css\" alternate=\"no\" media=\"all\"?>')

        svg_file.write('\n<svg baseProfile=\"full\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:ev=\"http://www.w3.org/2001/xml-events\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"'
                       ' width=\"100%\" height=\"100%\"'
                       ' viewBox=\"' + ' '.join((str(self.SVG_viewPort[0]), str(self.SVG_viewPort[1]), str(self.SVG_viewPort[2]), str(self.SVG_viewPort[3]))) + '\" preserveAspectRatio=\"xMinYMin\">')
        
        if embed_css in [True, 'True']:            
            svg_file.write('\n<defs><style type=\"text/css\"><![CDATA[\n')             
            svg_file.write(css_file)             
            svg_file.write('\n]]></style></defs>')   
        elif embed_css in ['IMPORT', 'import']:
            css_path = os.path.relpath(css_path, start=os.path.dirname(file_path)).replace('\\','/')
            svg_file.write('\n<defs><style type=\"text/css\">')
            svg_file.write("@import url(\'" + css_path + "\');</style></defs>") 
        else:
            svg_file.write('\n<defs></defs>')
             
        svg_file.write('\n<title>' + self.title + '-' + str(filenum) + '</title>')
        
        # Header SVG container
        song_header = ('\n<svg x=\"' + '%.2f'%self.SVG_viewPortMargins[0] + '\" y=\"' + '%.2f'%self.SVG_viewPortMargins[1] + \
                       '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%(self.SVG_viewPort[3]-self.SVG_viewPortMargins[1]) + '\">')
        
        x = 0
        y = self.SVG_text_height # Because the origin of text elements of the bottom-left corner

        if filenum==0:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"title\">' + self.title + '</text>'
            for i in range(len(self.headers[0])):
                y += 2*self.SVG_text_height
                song_header += '\n<text x=\"' + str(x)  + '\" y=\"' + str(y)  + '\" class=\"headers\">' + self.headers[0][i] + ' ' + self.headers[1][i] + '</text>'
        else:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"title\">' + self.title + ' (page ' + str(filenum+1) + ')</text>'
            
        # Dividing line
        y += self.SVG_text_height
        song_header += ('\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%(self.SVG_harp_spacings[1]/2.0) + '\">'
                        '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                        '\n</svg>')
        y += self.SVG_text_height
        
        song_header += '\n</svg>'

        svg_file.write(song_header)

        # Song SVG container
        ysong = y
        song_render = '\n<svg x=\"' + '%.2f'%self.SVG_viewPortMargins[0] + '\" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%(self.SVG_viewPort[3]-y) + '\" class=\"song\">'
        y = 0 #Because we are nested in a new SVG
        x = 0
        
        instrument_index = 0
        #end_row = min(start_row+self.maxLinesPerFile,len(self.lines))
        end_row = len(self.lines)
        for row in range(start_row, end_row):
            
            line = self.get_line(row)
            linetype = line[0].get_type()
            ncols = len(line)
            nsublines = int(1.0*ncols/self.maxIconsPerLine)
            
            if linetype == 'voice':
                ypredict = y + ysong + (self.SVG_text_height+self.SVG_harp_spacings[1]/2.0)*(nsublines+1) + self.SVG_harp_spacings[1]/2.0
            else:
                ypredict = y + ysong + (self.SVG_harp_size[1]+self.SVG_harp_spacings[1])*(nsublines+1) + self.SVG_harp_spacings[1]/2.0
                       
            if ypredict > (self.SVG_viewPort[3]-self.SVG_viewPortMargins[1]):
                end_row = row
                break
           
            line_render = ''
            sub_line = 0
            x = 0
            
            # Line SVG container            
            if linetype == 'voice':
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%self.SVG_text_height + '\" class=\"instrument-line line-' + str(row) + '\">' #TODO: modify height              
                y += self.SVG_text_height + self.SVG_harp_spacings[1]/2.0
            else:
                # Dividing line
                y += self.SVG_harp_spacings[1]/4.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%(self.SVG_harp_spacings[1]/2.0) + '\">'              
                song_render += '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                song_render += '\n</svg>'
                y += self.SVG_harp_spacings[1]/4.0
                
                y += self.SVG_harp_spacings[1]/2.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%self.SVG_harp_size[1] + '\" class=\"instrument-line line-' + str(row) + '\">'            
                y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1]/2.0
                
 
            for col in range(ncols):
                
                instrument = self.get_instrument(row,col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                if (int(1.0*col/self.maxIconsPerLine) - sub_line) > 0:
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0
                    #print('max reached at row=' + str(row) + ' col=' + str(col)) 
                    # New Line SVG placeholder
                    if linetype == 'voice':
                         #TODO: check text height and position
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%self.SVG_text_height + '\" class=\"instrument-line line-' + str(row) + '-' + str(sub_line) + '\">'
                        y += self.SVG_text_height + self.SVG_harp_spacings[1]/2.0
                    else:
                        y += self.SVG_harp_spacings[1]/2.0
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.SVG_line_width + '\" height=\"' + '%.2f'%self.SVG_harp_size[1] + '\" class=\"instrument-line line-' + str(row) + '-' + str(sub_line) + '\">'          
                        y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1]/2.0
 
                # INSTRUMENT RENDER
                instrument_render = instrument.render_in_svg(x, '%.2f'%(100.0*self.SVG_harp_size[0]/self.SVG_line_width)+'%', '100%', self.harp_AspectRatio)
                
                # REPEAT
                if instrument.get_repeat()>0:
                    instrument_render += '\n<svg x=\"' + '%.2f'%(x+self.SVG_harp_size[0]) + '\" y=\"0%\" class=\"repeat\" width=\"' + '%.2f'%(100.0*self.SVG_harp_size[0]/self.SVG_line_width)+'%' + '\" height=\"100%\">'
                    instrument_render += '\n<text x=\"2%\" y=\"98%\" class=\"repeat\">x' + str(instrument.get_repeat()) + '</text></svg>'
                    x += self.SVG_harp_spacings[0]
               
                line_render += instrument_render
                instrument_index += 1              
                x += self.SVG_harp_size[0] + self.SVG_harp_spacings[0]
                  
            song_render += line_render
            song_render += '\n</svg>' # Close line SVG        
               
        song_render += '\n</svg>' # Close song SVG
        svg_file.write(song_render) 
            
        svg_file.write('\n</svg>') # Close file SVG
        
        #Open new file
        if end_row < len(self.lines):
            filenum, file_path = self.write_svg(file_path0, embed_css, css_path, end_row, filenum+1) 
        
        return filenum, file_path
    
    #TODO: support for triplets and quavers with different colors
    def write_png(self, file_path0, start_row=0, filenum=0):        
        def trans_paste(bg, fg, box=(0,0)):
            if fg.mode == 'RGBA':
                if bg.mode != 'RGBA':
                    bg = bg.convert('RGBA')
                fg_trans = Image.new('RGBA', bg.size)
                fg_trans.paste(fg,box,mask=fg)#transparent foreground
                return Image.alpha_composite(bg,fg_trans)
            else:
                new_img = bg.copy()
                new_img.paste(fg, box)
                return new_img    
                
        if filenum>self.maxFiles:
            print('\nYour song is too long. Stopping at ' + str(self.maxFiles) + ' files.')
            return filenum, file_path0

        if filenum>0:
            (file_base, file_ext) = os.path.splitext(file_path0)
            file_path = file_base + str(filenum) + file_ext
        else:
            file_path = file_path0        
                       
        # Determines png size as a function of the numer of chords per line        
        self.set_png_harp_size()
        harp_rescale = self.get_png_harp_rescale()
        song_render = Image.new('RGBA', self.png_size, self.png_color)
        
        
        # Horizontal line drawing, to be used several times later
        hr_line = Image.new('RGBA', (int(self.png_line_width), 3))
        draw = ImageDraw.Draw(hr_line)
        draw = draw.line(((0,1), (self.png_line_width,1)), fill=(150,150,150), width=1)

        #TODO: add headers, and update ysong

        x_in_png = int(self.png_margins[0])
        y_in_png = int(self.png_margins[0])

        if filenum==0:
            
            fnt = ImageFont.truetype(self.png_font, self.png_title_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0,0), self.title, font=fnt, fill=self.font_color)
            song_render = trans_paste(song_render, title_header, (x_in_png, y_in_png))
            y_in_png += h*2
            
            for i in range(len(self.headers[0])):
                fnt = ImageFont.truetype(self.png_font, self.png_font_size)
                h = self.get_png_text_height(fnt)
                header = Image.new('RGBA', (int(self.png_line_width), int(h)))
                draw = ImageDraw.Draw(header)
                draw.text((0,0), self.headers[0][i] + ' ' + self.headers[1][i], font=fnt, fill=self.font_color)
                song_render = trans_paste(song_render, header, (x_in_png, y_in_png))
                y_in_png += h*2
        else:
            fnt = ImageFont.truetype(self.png_font, self.png_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0,0), self.title + '(page ' + str(filenum+1) + ')', font=fnt, fill=self.font_color)
            song_render = trans_paste(song_render, title_header, (x_in_png, y_in_png))
            y_in_png += 2*h + self.png_harp_spacings[1]
            

        ysong = y_in_png
        instrument_index = 0
        end_row = len(self.lines)        
        
        # Creating a new song image, located at x_in_song, yline_in_song
        xline_in_song = x_in_png
        yline_in_song = ysong
        for row in range(start_row, end_row):
            
            line = self.get_line(row)
            linetype = line[0].get_type()
            ncols = len(line)
            nsublines = int(1.0*ncols/self.maxIconsPerLine) # to be changed
            
            if linetype == 'voice':
                ypredict = yline_in_song  + (self.png_lyric_height+self.png_harp_spacings[1]/2.0)*(nsublines+1) + self.png_harp_spacings[1]/2.0
            else:
                ypredict = yline_in_song  + (self.png_harp_size[1]+self.png_harp_spacings[1])*(nsublines+1) + self.png_harp_spacings[1]/2.0
                       
            if ypredict > (self.png_size[1]-self.png_margins[1]):
                end_row = row
                break   #Bottom of image is reached, pausing line rendering
                      
            sub_line = 0
            # Line            
            if linetype.lower() == 'voice':
                line_render = Image.new('RGBA', (int(self.png_line_width),int(self.png_lyric_height)), self.png_color)
            else:
                # Dividing line
                yline_in_song += self.png_harp_spacings[1]/4.0
                song_render.paste(hr_line,(int(xline_in_song),int(yline_in_song)))
                yline_in_song += hr_line.size[1] + self.png_harp_spacings[1]/2.0
                
                line_render = Image.new('RGBA', (int(self.png_line_width),int(self.png_harp_size[1])), self.png_color)
             
            # Creating a new instrument image, starting at x=0 (in line) and y=0 (in line)
            x = 0
            y = 0
            for col in range(ncols):
                
                instrument = self.get_instrument(row,col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                if x + self.png_harp_size[0] + self.png_harp_spacings[0]/2.0 > self.png_line_width:
                    x = 0
                    song_render = trans_paste(song_render, line_render, (int(xline_in_song),int(yline_in_song)))
                    yline_in_song += line_render.size[1] + self.png_harp_spacings[1]/2.0
                    if linetype != 'voice':
                        yline_in_song += self.png_harp_spacings[1]/2.0 
                    
                    sub_line += 1
                    #print('max reached at row=' + str(row) + ' col=' + str(col)) 
                    # New Line
                    if linetype.lower() == 'voice':
                        line_render = Image.new('RGBA', (int(self.png_line_width),int(self.png_lyric_height)), self.png_color)
                    else:
                        line_render = Image.new('RGBA', (int(self.png_line_width),int(self.png_harp_size[1])), self.png_color)
 
                # INSTRUMENT RENDER
                instrument_render = instrument.render_in_png(harp_rescale)
                line_render = trans_paste(line_render, instrument_render,(int(x),int(y)))
                x += self.png_harp_size[0]
                
                # REPEAT                
                if instrument.get_repeat()>0:
                    repeat_im = instrument.get_repeat_png(self.png_harp_spacings[0], harp_rescale)
                    line_render = trans_paste(line_render, repeat_im,(int(x),int(y)))
                    x += repeat_im.size[0]
               
                x += self.png_harp_spacings[0]
                
                instrument_index += 1              
             
            song_render = trans_paste(song_render, line_render,(int(xline_in_song),int(yline_in_song))) # Paste line in song
            yline_in_song += line_render.size[1] + self.png_harp_spacings[1]/2.0         
            if linetype != 'voice':
                yline_in_song += self.png_harp_spacings[1]/2.0 
          
        song_render.save(file_path,dpi=self.png_dpi, compress_level=self.png_compress)
        
        song_render.show()
        
        #Open new file
        if end_row < len(self.lines):
            filenum, file_path = self.write_png(file_path0, end_row, filenum+1) 
        
        return filenum, file_path
        