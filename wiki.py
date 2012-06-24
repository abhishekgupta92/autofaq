import re
import params
import os
import urllib
import errno

class Wiki:
    _subject="Britney Spears"
    _fileRead = "data/wiki.html"
    _fileWrite = "data/wiki.txt"
    _mult = 0.8
    _minLength = 30
    _bornOn=(None,None,None)

    def __init__ (self,subject):
        self._subject = subject
        self._fileRead = params.tempStorage+"/"+self._subject+".html"
        self._fileWrite = params.tempStorage+"/"+self._subject+".txt"

    def getPage (self):
        try:
            os.makedirs(params.tempStorage)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise
        urllib.urlretrieve("http://en.wikipedia.org/w/api.php?format=xml&action=query&titles="+self._subject+"&prop=revisions&rvprop=content",self._fileRead)

    def getRawText(self):
        fread=open(self._fileRead,'r')
        lines=fread.readlines() #Returns a list of lines
        fread.close()
        
        #Remove Unnecessary tags
        lines=map(lambda str : re.sub(r'<[^>]+>',"",str), lines)
        lines=map(lambda str : re.sub(r'<!--[\\s\\S]*?-->','',str), lines)
        lines=map(lambda str : re.sub(r'<math>.*?</math>','',str), lines)
        lines=map(lambda str : re.sub(r'<nowiki>.*?</nowiki>','',str), lines)
        lines=map(lambda str : re.sub(r'<gallery>.*?</gallery>','',str), lines)
        lines=map(lambda str : re.sub(r'<code>.*?</code>','',str), lines)
        lines=map(lambda str : re.sub(r'<source>.*?</source>','',str), lines)

        #Subsitute [\1|\2] by \2
        lines=map(lambda str : re.sub(r'\[\[([^|\]]+?)\|(.+?)\]\]', r'\2', str), lines)
        #Substitute [\1] by \1
        lines=map(lambda str : re.sub(r'\[\[([^\]]+?)\]\]', r'\1', str), lines)
        #Replace remaining [] by ""
        lines=map(lambda str : re.sub(r'\[[^\]]+\]',r'',str), lines)
        #Remove anything between {}
        lines=map(lambda str : re.sub(r'\{\{([^}]+?)\}\}','',str), lines)
        #Remove Tables {| |}
        lines=filter(lambda str : '||' not in str, lines)
        lines=filter(lambda str : '{|' not in str, lines)
        lines=filter(lambda str : '|}' not in str, lines)
        lines=filter(lambda str : '|-' not in str, lines)
        
        lines=map(lambda str : re.sub(r'\{\{([^}]+?)\}\}','',str), lines)
        #Remove anything between <>
        lines=map(lambda str : re.sub(r'\<([^>]+?)\>','',str), lines)

        lines=map(lambda str : re.sub(r"\'\'([^']+?)\'\'", r'\1', str), lines)

        #Replace with standard characters
        lines = map(lambda str : re.sub(r'&lt(.+?)&gt', '', str), lines)
        lines=map(lambda str:re.sub(r'&quot','"',str),lines)
        lines=map(lambda str:re.sub(r'&amp',' and ',str),lines)
        lines=map(lambda str:re.sub(r'nbsp',' ',str),lines)
        lines=map(lambda str:re.sub(r'\x96','-',str),lines)
        lines=map(lambda str:re.sub(r'\xe2\x80\x93','-',str),lines)

        arr=lines
        lines=[]

        #}} in next line? Append it with the previous line
        for line in arr:
            if re.search(r'}}',line):
                lines[len(lines)-1]+=line
            else:
                lines.append(line)

        lines=map(lambda str : re.sub(r'\{\{([^}]+?)\}\}','',str), lines)

        #Break the lines about full stops
        arr=[]
        for line in lines:
            tokens=line.split(". ")
            for t in tokens:
                arr.append(t+"\n")
        lines = arr

        #Join the lines - reduce function
        arr=[]
        for line in lines:
            tokens=line.split('." ')
            for t in tokens:
                arr.append(t+"\n")
        lines = arr

        lines=self.removeAfter(lines,"References")
        lines=self.removeAfter(lines,"See also")
        lines=self.removeSections(lines,"References")
        lines=self.removeSections(lines,"Further reading")
        lines=self.removeSections(lines,"References")
        lines=self.removeSections(lines,"External links")
        lines=self.removeSections(lines,"==")

        #remove thumbnails links
        lines=filter(lambda line : not re.search('thumb',line),lines)

        lines=map(lambda line: filter(lambda c:self.ischar(c),line), lines)

        #Remove empty lines
        lines=filter(lambda line : line != "\n",lines)

        lines=map(lambda l:l.replace("\n",""),lines)
        lines=filter(lambda l:l!="",lines)
        lines=filter(lambda l:len(l)>25, lines)
        return lines

    def ischar(self,char):
        if char==" ":
            return True
        elif re.match(r'[A-Za-z0-9]',char+""):
            return True
        
    def removeSections(self, lines, str):
        lines=filter(lambda line: line.find(str) == -1,lines)
        return lines

        mainheading=""
        subHeading=""
        for i,line in enumerate(lines):
            try:
                subHeading=re.match(r"===(.+)===",line).group(1)
            except:
                try:
                    mainHeading=re.match(r"==(.+)==",line).group(1)
                    subHeading=mainHeading
                except:
                    pass
            if (len(line) < self._minLength) or (mainHeading.find(str) or subHeading.find(str)):
                lines[i]=""
        return lines

    def removeAfter(self,lines,str):
        lines=filter(lambda line: line.find(str) == -1,lines)
        return lines

        mainheading=""
        subHeading=""
        entry=False
        for i,line in enumerate(lines):
            try:
                subHeading=re.match(r"===(.+)===",line).group(1)
            except:
                try:
                    mainHeading=re.match(r"==(.+)==",line).group(1)
                    subHeading=mainHeading
                except:
                    pass
            if mainHeading.find(str) or subHeading.find(str):
                entry=True
            if entry==True:
                lines[i]=""
        return lines
        

if __name__ == "__main__":
    subject="Google Summer of Code"
    
    pWiki = Wiki(subject)
    pWiki.getPage()

    lines=pWiki.getRawText()

    print lines
