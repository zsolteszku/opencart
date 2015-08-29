<?php echo $header; ?><?php echo $column_left; ?>
<div id="content">
  <div class="page-header">
    <div class="container-fluid">
      <div class="pull-right">
          <a href="<?php echo $process; ?>" data-toggle="tooltip" title="Press to start the import process" class="btn btn-primary"><i class="fa fa-upload"></i></a>
      </div>
      <h1><?php echo $heading_title; ?></h1>
      <ul class="breadcrumb">
        <?php foreach ($breadcrumbs as $breadcrumb) { ?>
        <li><a href="<?php echo $breadcrumb['href']; ?>"><?php echo $breadcrumb['text']; ?></a></li>
        <?php } ?>
      </ul>
    </div>
  </div>
  <div class="container-fluid">
    <?php if ($error_warning) { ?>
    <div class="alert alert-danger"><i class="fa fa-exclamation-circle"></i> <?php echo $error_warning; ?>
      <button type="button" class="close" data-dismiss="alert">&times;</button>
    </div>
    <?php } ?>
    <?php if ($success) { ?>
    <div class="alert alert-success"><i class="fa fa-check-circle"></i> <?php echo $success; ?>
      <button type="button" class="close" data-dismiss="alert">&times;</button>
    </div>
    <?php } ?>
    <div class="panel panel-default">
      <div class="panel-heading">
        <h3 class="panel-title"><i class="fa fa-list"></i> Import</h3>
      </div>
      <div class="panel-body">
        <form action="<?php echo $process; ?>" method="post" enctype="multipart/form-data" id="form-import" class="form-horizontal">
            <div class="form-group">
                <label class="form-label col-sm-2" for="selectedFile">Csv file</label>
                <div class="col-sm-10">
                    <select class="form-control" id="selectedFile" name="selectedFile" >
                        <?php foreach ($files as $file) { ?>
                        <option value="<?php echo $file; ?>"><?php echo $file; ?></option>
                        <?php } ?>
                    </select>
                </div>  
            </div>
            <button type="submit" data-toggle="tooltip" title="Press to start the import process" class="btn btn-primary submit"><i class="fa fa-play"></i>&nbsp Import </button>
        </form>


      </div>
    </div>
    <?php if( count($newManufacturers) > 0 || count($updatedManufacturers) > 0 ) { ?>
    <div class="panel panel-default">
      <div class="panel-heading">
        <h3 class="panel-title"><i class="fa fa-list"></i> Import result</h3>
      </div>
      <div class="panel-body">
           <?php if ( $newManufacturers ) { ?>
          <div class="table-responsive">
                <table class="table table-bordered table-hover">
                    <caption>Added Manufacturers</caption>
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Name</th>
                        </tr>
                    </thead>
                    <?php foreach ($newManufacturers as $manufacturer) { ?>
                        <tr>
                            <td>
                                  <?php echo $manufacturer['manufacturer_id'] ?> 
                            </td> 
                            <td>
                                  <?php echo $manufacturer['name'] ?> 
                            </td>
                        </tr>
                    <?php } ?>
                </table>
            </div>
          <?php } ?>
         
          <?php if ( $updatedManufacturers ) { ?>
          <div class="table-responsive">
                <table class="table table-bordered table-hover">
                    <caption>Updated Manufacturers</caption>
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Name</th>
                        </tr>
                    </thead>
                    <?php foreach ($updatedManufacturers as $manufacturer) { ?>
                        <tr>
                            <td>
                                  <?php echo $manufacturer['manufacturer_id'] ?> 
                            </td> 
                            <td>
                                  <?php echo $manufacturer['name'] ?> 
                            </td>
                        </tr>
                    <?php } ?>
                </table>
            </div>
          <?php } ?>
      </div>
    </div>
    <?php } ?>
  </div>
</div>
<?php echo $footer; ?>