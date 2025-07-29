import sys,os,re
from typing import List

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from util.BluesMailer import BluesMailer  
from type.command.Command import Command
from util.BluesFiler import BluesFiler

class EmailCmd(Command):

  _mailer = BluesMailer.get_instance()

  def execute(self):
    payload = self.get_payload()
    stdout = self._mailer.send(payload)
    self._context['email'] = stdout
    if stdout.code==200:
      message = f'[{self.__class__.__name__}] Managed to send a notification email'
      self._logger.info(message)
    else:
      message = f'[{self.__class__.__name__}] Failed to send a notification email'
      self._logger.error(message)
      
  def get_payload(self)->dict:
    entities = None
    output:STDOut = self._context.get('output')
    if output and output.code==200:
      entities = output.data

    title = self._get_subject(entities)
    content = self._get_content(title,entities)
    subject = BluesMailer.get_title_with_time(title)
    return {
      'subject':subject,
      'content':content,
      'images':None,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }


  def _get_subject(self,entities:List[dict])->str:
    subject = ''
    if entities:
      count = len(entities)
      subject = f'Managed to crawl and persist {count} entities'
    else:
      subject = 'Failed to crawl and persist entities'
    return subject

  def _get_content(self,title:str,entities:List[dict])->str:
    para = self._get_para(entities)
    urls = self._get_urls()
    detail = self._get_log()
    return BluesMailer.get_html_body(title,para,urls,detail)
  
  def _get_urls(self):
    href = self._logger.file
    text = f'Local log file: {href}'
    return [
      {
        'href':href,
        'text':text,
      }
    ]
    
  def _get_log(self):
    file = self._logger.file
    separator = self._logger.separator
    content = BluesFiler.read(file)
    if content:
      # retain the latest one
      items = content.split(separator)
      non_empty_items = [item.strip() for item in items if item.strip()]
      content = non_empty_items[-1] if non_empty_items else content
      
      # break line
      content = content.replace('\n','<br/>')
      # dash line
      pattern = r'[-=]{10,}'
      content = re.sub(pattern, '----------', content)
    return content
  
  def _get_para(self,entities:List[dict])->str:
    para = ''
    if not entities:
      return 'Failed to crawl entities'

    para = f'There are {len(entities)} entities:<br/>'

    for idx,entity in enumerate(entities):
      para+=f"{idx+1}. {entity['material_title']}</br>"
    return para