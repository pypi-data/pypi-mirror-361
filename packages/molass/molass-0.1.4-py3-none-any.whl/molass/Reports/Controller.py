"""
    Reports.Controller.py
"""
import os
import logging

class Controller:
    """
    Controller class for managing report generation in MOLASS.

    This class corresponds to the legacy SerialExecuter class in molass_legacy.SerialAnalyzer.SerialController.
    """
    def __init__(self, parallel=False):
        self.logger = logging.getLogger(__name__)
        self.temp_folder = ".temp"
        self.make_temp_folder()
        self.excel_is_available = True
        self.more_multicore = parallel and os.cpu_count() > 4
        if self.excel_is_available:
            if self.more_multicore:
                from molass_legacy.ExcelProcess.ExcelTeller import ExcelTeller
                self.teller = ExcelTeller(log_folder=self.temp_folder)
                self.logger.info('teller created with log_folder=%s', self.temp_folder)
                self.excel_client = None
            else:
                from molass_legacy.KekLib.ExcelCOM import CoInitialize, ExcelComClient
                self.teller = None
                CoInitialize()
                self.excel_client = ExcelComClient()
            self.result_wb = None
        else:
            from openpyxl import Workbook
            self.excel_client = None
            self.result_wb = Workbook()

    def make_temp_folder( self ):
        from molass_legacy.KekLib.BasicUtils import clear_dirs_with_retry
        try:
            clear_dirs_with_retry([self.temp_folder])
        except Exception as exc:
            from molass_legacy.KekLib.ExceptionTracebacker import  ExceptionTracebacker
            etb = ExceptionTracebacker()
            self.logger.error( etb )
            raise exc
    
    def stop(self):
        if self.teller is None:
            self.cleanup()
        else:
            self.teller.stop()
    
    def cleanup(self):
        from molass_legacy.KekLib.ExcelCOM import CoUninitialize
        self.excel_client.quit()
        self.excel_client = None
        CoUninitialize()

    def stop_check(self):
        """
        Check if the controller should stop.
        """
        self.logger.warning('stop_check is not implemented in Controller.')