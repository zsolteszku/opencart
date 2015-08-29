<?php

define("ARTIST_NAME", "Artist");
define("TITLE", "Title");
define("YEAR", "Year");
define("TECH", "Tech");

class ControllerCatalogImport extends Controller {
	private $error = array();
    private $success = '';

    private $newManufacturers = array();
    private $updatedManufacturers = array();
    

	public function index() {
		$this->language->load('catalog/import');

		$this->document->setTitle($this->language->get('heading_title'));

        $this->load->model('catalog/product');
        $this->load->model('catalog/import');
        
        $this->getList();
	}

	public function process() {
		$this->language->load('catalog/import');

		$this->document->setTitle($this->language->get('heading_title'));

		$this->load->model('catalog/import');

        $this->load->model('catalog/product');

		if (($this->request->server['REQUEST_METHOD'] == 'POST') &&  $this->validateFile()) {
            
            $selectedFile = $this->request->post['selectedFile'];
            $data['selectedFile'] = $selectedFile;
            $data['success'] = $selectedFile;

            $csvData = $this->csv_to_array(DIR_DOWNLOAD . $selectedFile);

            $this->processCsvData($csvData);

            //$this->model_catalog_product->addProduct($this->request->post);

            //$this->response->redirect($this->url->link('catalog/import', 'token=' . $this->session->data['token'] . '&imported='.$selectedFile, 'SSL'));
        }

        $this->getList();
	}

    private function processCsvData($table){

        $this->load->model('catalog/manufacturer');
        $this->load->model('setting/store');
        $stores = $this->model_setting_store->getStores();

        $storeId = null;
        if(count($stores) > 0){
            $storeId =  $stores[0]->id;
        }

        $lastArtist = null;
        foreach ($table as $row)
        {
            if(!$row[ARTIST_NAME]){
                $row[ARTIST_NAME] = $lastArtist;    
            }
            
            $filterData['filter_name'] = $row[ARTIST_NAME];
            $filterData['limit'] = 1;
            $filterData['start'] = 0;
        	$dbRows = $this->model_catalog_manufacturer->getManufacturers($filterData);
            $maufacturerId = null;
            if(isset($dbRows) && $dbRows && count($dbRows) > 0){
                if($row[ARTIST_NAME] != $lastArtist){
                    //update
                    // pushing into the array
                    $this->updatedManufacturers[] = $dbRows[0];
                }
                
            }else{
                //insert
                $insertData['name'] = $row[ARTIST_NAME];
                $insertData['sort_order'] = 0;
                $insertData['manufacturer_store'][0] = $storeId;
                $insertData['keyword'] = $row[ARTIST_NAME];
                $maufacturerId = $this->model_catalog_manufacturer->addManufacturer($insertData);

                $insertData['manufacturer_id'] = $maufacturerId;

                $this->newManufacturers[] = $insertData;
            }

            $lastArtist = $row[ARTIST_NAME];
        }
    }

    /**
     * Convert a comma separated file into an associated array.
     * The first row should contain the array keys.
     * 
     * Example:
     * 
     * @param string $filename Path to the CSV file
     * @param string $delimiter The separator used in the file
     * @return array
     * @link http://gist.github.com/385876
     * @author Jay Williams <http://myd3.com/>
     * @copyright Copyright (c) 2010, Jay Williams
     * @license http://www.opensource.org/licenses/mit-license.php MIT License
     */
    private function csv_to_array($filename='', $delimiter=';')
    {
        if(!file_exists($filename) || !is_readable($filename))
            return FALSE;
        
        $header = NULL;
        $data = array();
        if (($handle = fopen($filename, 'r')) !== FALSE)
        {
            while (($row = fgetcsv($handle, 1000, $delimiter)) !== FALSE)
            {
                //echo "<p>$row[1]</p></br>";
                if(!$header)
                    $header = $row;
                else
                    $data[] = array_combine($header, $row);
            }
            fclose($handle);
        }
        return $data;
    }

    private function setNotifications($dataArray){

        if (isset($this->error['warning'])) {
			$dataArray['error_warning'] = $this->error['warning'];
		} else {
			$dataArray['error_warning'] = '';
		}

		if (isset($this->error['name'])) {
			$dataArray['error_name'] = $this->error['name'];
		} else {
			$dataArray['error_name'] = array();
		}

		if (isset($this->error['meta_title'])) {
			$dataArray['error_meta_title'] = $this->error['meta_title'];
		} else {
			$dataArray['error_meta_title'] = array();
		}

		if (isset($this->error['model'])) {
			$dataArray['error_model'] = $this->error['model'];
		} else {
			$dataArray['error_model'] = '';
		}

        if (isset($this->session->data['success'])) {
			$dataArray['success'] = $this->session->data['success'];

			unset($this->session->data['success']);
		} else {
			$dataArray['success'] = '';
		}

        $dataArray['success'] = $this->success;

        return $dataArray;
    }

	protected function getList() {
		
		$data['breadcrumbs'] = array();

		$data['breadcrumbs'][] = array(
			'text' => $this->language->get('text_home'),
			'href' => $this->url->link('common/dashboard', 'token=' . $this->session->data['token'], 'SSL')
		);

		$data['breadcrumbs'][] = array(
			'text' => $this->language->get('heading_title'),
			'href' => $this->url->link('catalog/import', 'token=' . $this->session->data['token'] . $url, 'SSL')
		);

		$data['process'] = $this->url->link('catalog/import/process', 'token=' . $this->session->data['token'] . $url, 'SSL');
		
		$data['header'] = $this->load->controller('common/header');
		$data['column_left'] = $this->load->controller('common/column_left');
		$data['footer'] = $this->load->controller('common/footer');
        
        //$files =   array_diff(scandir(DIR_DOWNLOAD), array('..', '.'));
        $files =   array_filter(scandir(DIR_DOWNLOAD), function($val) { return !is_dir($val); });
        
        $data['files'] = $files;

        $data['newManufacturers'] = $this->newManufacturers;
        $data['updatedManufacturers'] = $this->updatedManufacturers;

        $finalData = $this->setNotifications($data);
		$this->response->setOutput($this->load->view('catalog/import.tpl', $finalData));
	}

	protected function validateFile() {
		return !$this->error;
	}
}
