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
        <form action="<?php echo $process; ?>" method="post" enctype="multipart/form-data" id="form-import">
          <label>Csv file</label> <input type="file" accept=".csv" />
           
            <p><?php echo $testString ?></p>
            <p><?php echo $testString2 ?></p>

          <br />
          <a href="<?php echo $process; ?>" data-toggle="tooltip" title="Press to start the import process" class="btn btn-primary"><i class="fa fa-upload"></i></a>
        </form>
      </div>
    </div>
  </div>
</div>
<?php echo $footer; ?>