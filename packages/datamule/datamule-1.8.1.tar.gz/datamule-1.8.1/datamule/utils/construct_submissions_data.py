import zipfile
import json
import csv
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import urllib.request

headers = {'User-Agent': 'John Smith johnsmith@gmail.com'}

def process_file_batch(zip_file, filenames_batch):
    """Process a batch of files from the zip archive"""
    batch_filings = []
    
    for filename in filenames_batch:
        if not filename.startswith('CIK'):
            continue
            
        try:
            # Extract CIK from filename
            cik = int(filename.split('.')[0].split('-')[0][3:])
            
            # Read raw bytes and parse JSON
            with zip_file.open(filename) as file:
                raw_data = file.read()
                submissions_dct = json.loads(raw_data)
            
            # Handle different file types
            if 'submissions' in filename:
                filings_data = submissions_dct
            else:
                filings_data = submissions_dct['filings']['recent']
            
            # Extract required data
            accession_numbers = filings_data['accessionNumber']
            filing_dates = filings_data['filingDate']
            forms = filings_data['form']
            
            # Create filing records for this file
            for j in range(len(accession_numbers)):
                filing_record = {
                    'accessionNumber': int(accession_numbers[j].replace('-','')),
                    'filingDate': filing_dates[j],
                    'submissionType': forms[j],
                    'cik': cik
                }
                batch_filings.append(filing_record)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    return batch_filings

def write_csv_chunk(output_path, filings_data, is_first_write, write_lock):
    """Thread-safe CSV writing with lock"""
    with write_lock:
        if is_first_write:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = ['accessionNumber', 'filingDate', 'submissionType', 'cik']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filings_data)
        else:
            with open(output_path, 'a', newline='') as csvfile:
                fieldnames = ['accessionNumber', 'filingDate', 'submissionType', 'cik']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerows(filings_data)

def construct_submissions_data(output_path, submissions_zip_path=None, max_workers=4, batch_size=100):
    """Creates a list of dicts of every accession number, with filing date, submission type, and ciks"""
    
    if submissions_zip_path is None:
        url = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
        
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'submissions.zip')
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            
            with open(zip_path, 'wb') as f, tqdm(
                desc="Downloading",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        submissions_zip_path = zip_path
    
    # Keep zip file open throughout processing
    with zipfile.ZipFile(submissions_zip_path, 'r') as zip_file:
        # Get all CIK filenames
        all_filenames = [f for f in zip_file.namelist() if f.startswith('CIK')]
        
        print(f"Processing {len(all_filenames)} files with {max_workers} workers...")
        
        # Create batches of filenames
        filename_batches = []
        for i in range(0, len(all_filenames), batch_size):
            batch = all_filenames[i:i + batch_size]
            filename_batches.append(batch)
        
        # Setup for threading
        write_lock = threading.Lock()
        total_filings = 0
        is_first_write = True
        
        # Process batches with thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batch jobs
            future_to_batch = {
                executor.submit(process_file_batch, zip_file, batch): i 
                for i, batch in enumerate(filename_batches)
            }
            
            # Process results with progress bar
            with tqdm(total=len(filename_batches), desc="Processing batches", unit="batch") as pbar:
                for future in future_to_batch:
                    try:
                        batch_filings = future.result()
                        
                        if batch_filings:  # Only write if we have data
                            write_csv_chunk(output_path, batch_filings, is_first_write, write_lock)
                            is_first_write = False
                            total_filings += len(batch_filings)
                        
                        pbar.update(1)
                        pbar.set_postfix({
                            'filings': total_filings,
                            'files': len(filename_batches[future_to_batch[future]])
                        })
                        
                    except Exception as e:
                        print(f"Error processing batch: {e}")
                        pbar.update(1)
    
    print(f"Complete! Processed {total_filings} total filings")
    print(f"Data saved to {output_path}")