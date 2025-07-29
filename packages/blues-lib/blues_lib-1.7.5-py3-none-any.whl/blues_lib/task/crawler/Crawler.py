import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.BhvExecutor import BhvExecutor
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser 
from logger.LoggerFactory import LoggerFactory

class Crawler():

  def __init__(self,model:Model,browser:Browser,keep_alive:bool=True) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    @param keep_alive {bool} : whether to keep the browser alive after crawl
    '''
    self._model = model
    self._browser = browser
    self._keep_alive = keep_alive
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()

  def crawl(self)->STDOut:
    
    try:
      executor = BhvExecutor(self._model,self._browser)
      stdout=  executor.execute()
      return self._output(stdout)
    except Exception as e:
      message = f'[Crawler] Failed to crawl any entities - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    finally:
      if self._browser and not self._keep_alive:
        self._browser.quit()
        
  def _output(self,crawl_out:STDOut)->STDOut:
    if crawl_out.code != 200:
      message = f'[Crawler] Failed to crawl - {crawl_out.message}'
      self._logger.error(message)
    else:
      message = f'[Crawler] Managed to crawl - a {type(crawl_out.data)} data'
      self._logger.info(message)

    return crawl_out