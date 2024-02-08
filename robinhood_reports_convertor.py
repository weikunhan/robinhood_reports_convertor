# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2024 Weikun Han
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================
""" Robinhood reports convertor

Welcome to use the Robinhood reports convertor!
Please check the README file if have any question.

Author:
Weikun Han <weikunhan@gmail.com>
"""

import argparse
import json
import numpy as np
import os
import pandas as pd
import sys
from collections import defaultdict
from tqdm import tqdm
from typing import Any
from typing import Union
from utils.common_util import convert_col_type_dataframe
from utils.common_util import initial_log

STOCK_EXCEL_COL_NAME_LIST = [
    'Date', 'Type', 'Quantity', 'Price', 'Amount', 'Profit']
OPTION_EXCEL_COL_NAME_LIST = [
    'Date', 'Description', 'Type', 'Quantity', 'Price', 'Amount', 'Profit']    
INSTRUMENT_TRANSCODE_CONFIG_PATCH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    'configs',
    'instrument_transcode_config.json')

def convert_string_value(string_value: str) -> float:
    """Convert string value to float

    Args:

    Returns:

    Raises:

    """

    if '$' in string_value:
        string_value = string_value.replace('$', '')

    if '(' in string_value:
        string_value = string_value.replace('(', '')

    if ')' in string_value:
        string_value = string_value.replace(')', '')

    if ',' in string_value:
        string_value = string_value.replace(',', '')    

    return float(string_value)

def get_option_dict(
    instrument_config_dict: dict,
    date_value: str,
    transcode_value: str,
    logger: Any
) -> tuple:
    """Get option dict for main function

    Args:

    Returns:

    Raises:

    """   

def get_stock_dict(
    instrument_config_dict: dict,
    stock_data_dict: dict,
    row: pd.DataFrame,
    date_value: str,
    transcode_value: str,
    logger: Any
) -> dict:
    """Get stock dict for main function

    Args:

    Returns:

    Raises:

    """   

    quantity_value = row['Quantity']
    price_value = 0.0
    amount_value = 0.0

    if not pd.isnull(row['Price']) and row['Price'] != '':
        price_value = convert_string_value(row['Price'])    

    if not pd.isnull(row['Amount']) and row['Amount'] != '':
        amount_value = convert_string_value(row['Amount'])    

    if instrument_config_dict['stock'][transcode_value][0]: 
        key_value = f'{date_value}-{transcode_value}-{price_value}' 
    else:
        key_value = f'{date_value}-{transcode_value}' 

    factor_value = instrument_config_dict['stock'][transcode_value][1]
    stock_data_dict[key_value] = (
        stock_data_dict[key_value][0] + factor_value * quantity_value,
        stock_data_dict[key_value][1] + factor_value * amount_value)  

    return stock_data_dict

def get_stock_and_option_dict(
    instrument_config_dict: dict,
    instrument_df: pd.DataFrame,
    logger: Any
) -> tuple:
    """Get stock and option dict from grouped dataframe

    starting from Python 3.7, the dict also maintains insertion order

    Args:

    Returns:

    Raises:

    """

    stock_data_dict = defaultdict(lambda: (0, 0.0))
    option_data_dict = defaultdict(lambda: (0, 0.0))

    for index, row in tqdm(instrument_df.iterrows(), 
                           desc='Converting in progress'):
        date_value = row["Activity Date"]
        transcode_value = row['Trans Code']
        
        if transcode_value in instrument_config_dict['stock']:
            stock_data_dict = get_stock_dict(
                instrument_config_dict, 
                stock_data_dict,
                row, 
                date_value, 
                transcode_value, 
                logger)
        elif transcode_value in instrument_config_dict['option']:   
            pass
        else:
            logger.warning(f'Found undefined transcode: {transcode_value}\n')

    return stock_data_dict, option_data_dict    

def save_option_result(
    instrument_config_dict: dict, 
    option_data_dict: dict, 
    output_csv_filepath: str, 
    logger: Any
) -> None:   
    """Save option result into special format

    Args:

    Returns:

    Raises:

    """

def save_stock_result(
    instrument_config_dict: dict,
    stock_data_dict: dict, 
    output_xlsx_filepath: str, 
    logger: Any,
) -> None:   
    """Save stock result into special format

    Args:

    Returns:

    Raises:

    """

    quantity_sum_value = 0
    amount_sum_value = 0.0
    stock_data_list = []
        
    for key, value in reversed(stock_data_dict.items()):
        date_value = key.split('-')[0]
        transcode_value = key.split('-')[1]
        quantity_value = value[0]
        amount_value = value[1]

        if instrument_config_dict['stock'][transcode_value][0]: 
            price_value = key.split('-')[2]
            quantity_sum_value += quantity_value
            amount_sum_value += amount_value

            if quantity_sum_value != 0:
                stock_data_list.append([date_value,
                                        transcode_value,
                                        quantity_value,
                                        price_value,
                                        amount_value,
                                        ''])
            else:
                logger.info(f'Calculating profit on date: {date_value}...\n')
                stock_data_list.append([date_value,
                                        transcode_value,
                                        quantity_value,
                                        price_value,
                                        amount_value,
                                        -amount_sum_value])
                amount_sum_value = 0.0
        else:
            stock_data_list.append([date_value, 
                                    transcode_value, 
                                    '', 
                                    '',
                                    amount_value, 
                                    amount_value])
   
    stock_df = pd.DataFrame(stock_data_list, columns=STOCK_EXCEL_COL_NAME_LIST)   

    with pd.ExcelWriter(output_xlsx_filepath) as writer:
        stock_df.to_excel(writer, sheet_name='STOCK', index=False)

def main ():

    if not os.path.exists(args.data_files_path):
        os.makedirs(args.data_files_path)

    if not os.path.exists(args.log_files_path):
        os.makedirs(args.log_files_path)

    logger, logger_output_filepath = initial_log(args.log_files_path)
    input_csv_filepath = os.path.join(args.data_files_path, args.input_csv_name)  
    logger.info('=' * 80)
    logger.info('Start convertor execution')
    logger.info(f'The csv file load from: {input_csv_filepath}')
    logger.info(f'The log file saved into: {logger_output_filepath}')
    logger.info('=' * 80 + '\n')

    try:
        instrument_config_dict = json.loads(
            open(INSTRUMENT_TRANSCODE_CONFIG_PATCH).read())
    except Exception as e:
        logger.error(
            f'Failed config from from: {INSTRUMENT_TRANSCODE_CONFIG_PATCH}')
        logger.error(f'The detail error message: {e}')
        sys.exit(1) 

    try: 
        input_df = pd.read_csv(input_csv_filepath,
                               encoding='utf-8',
                               on_bad_lines='skip', 
                               header=0)
    except Exception as e:
        logger.error(f'Failed read csv from: {input_csv_filepath}')
        logger.error(f'The detail error message: {e}')
        sys.exit(1) 

    input_df = convert_col_type_dataframe(input_df, 'Quantity', 'int')  

    for instrument_value, instrument_df in input_df.groupby('Instrument'):
        msg = ('Converting robinhood stock and option reports for: '
               f'{instrument_value}...\n')
        logger.info(msg)
        stock_data_dict, option_data_dict = get_stock_and_option_dict(
            instrument_config_dict, instrument_df, logger)
        logger.info(f'Saving stock result for: {instrument_value}...\n')    
        save_stock_result(
            instrument_config_dict,
            stock_data_dict,
            os.path.join(args.data_files_path, f'{instrument_value}.xlsx'),
            logger)
        logger.info(f'Saving option result for: {instrument_value}...\n')
        save_option_result(
            instrument_config_dict,
            option_data_dict,
            os.path.join(args.data_files_path, f'{instrument_value}.xlsx'),
            logger)

    logger.info('=' * 80)
    logger.info('Finished convertor execution')
    logger.info(f'The xlsx files saved into: {args.data_files_path}')
    logger.info(f'The log file saved into: {logger_output_filepath}')
    logger.info('=' * 80 + '\n')
               
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Robinhood reports convertor')
    parser.add_argument('-i', '--input-csv-name', type=str,
                        required=True,
                        help='Input report file name')
    parser.add_argument('-d', '--data-files-path', type=str,
                        default=os.path.join(
                            os.path.abspath(os.path.dirname(__file__)), 'data'),
                        required=False,
                        help='Data files input and output path')
    parser.add_argument('-l', '--log-files-path', type=str,
                        default=os.path.join(
                            os.path.abspath(os.path.dirname(__file__)), 'logs'),
                        required=False,
                        help='Log files save path')
    args = parser.parse_args()

    print('-' * 80 + '\n')
    print('Welcome to use the Robinhood reports convertor!\n')
    print('Please check the README file if have any question.\n')
    print('-' * 80 + '\n')
    main()