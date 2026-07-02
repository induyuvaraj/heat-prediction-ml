// Study Area for LANDSAT DATA

var kanchipuram = ee.Geometry.Point([79.70, 12.83]).buffer(20000);

// Function to prepare yearly collection
function getYearData(year) {
  
  var startDate = ee.Date.fromYMD(year, 4, 1);
  var endDate = ee.Date.fromYMD(year, 5, 31);
  
  var dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(kanchipuram)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUD_COVER', 10))
    .mean()
    .clip(kanchipuram);
  
  var bands = dataset.select(['ST_B10','SR_B4','SR_B5']);
  
  return bands.sample({
    region: kanchipuram,
    scale: 30,
    numPixels: 5000,
    geometries: true
  });
}

Export.table.toDrive({
  collection: getYearData(2023),
  description: 'Landsat_Data_2023',
  fileNamePrefix: 'Landsat_Data_2023',
  fileFormat: 'CSV'
});



// Study area for NDBI DATA

var kanchipuram = ee.Geometry.Point([79.70, 12.83]).buffer(20000);

function exportNDBI(year) {
  
  var startDate = ee.Date.fromYMD(year, 4, 1);
  var endDate = ee.Date.fromYMD(year, 5, 31);
  
  var s2 = ee.ImageCollection('COPERNICUS/S2_SR')
    .filterBounds(kanchipuram)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',10))
    .select(['B8','B11'])
    .median()
    .clip(kanchipuram);

  var ndbi = s2.normalizedDifference(['B11','B8']).rename('NDBI');

  var samples = ndbi.sample({
    region: kanchipuram,
    scale: 10,
    numPixels: 5000,
    geometries: true
  });

  Export.table.toDrive({
    collection: samples,
    description: 'Sentinel_NDBI_' + year,
    fileNamePrefix: 'Sentinel_NDBI_' + year,
    fileFormat: 'CSV'
  });
}

exportNDBI(2023);


// Study area for NBVI DATA

var kanchipuram = ee.Geometry.Point([79.70, 12.83]).buffer(20000);

function exportNDVI(year) {
  
  var startDate = ee.Date.fromYMD(year, 4, 1);
  var endDate = ee.Date.fromYMD(year, 5, 31);
  
  var s2 = ee.ImageCollection('COPERNICUS/S2_SR')
    .filterBounds(kanchipuram)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    .select(['B4','B8'])
    .median()
    .clip(kanchipuram);
  
  var ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI');
  
  var sample = ndvi.sample({
    region: kanchipuram,
    scale: 10,
    numPixels: 5000,
    geometries: true
  });
  
  Export.table.toDrive({
    collection: sample,
    description: 'Sentinel_NDVI_' + year,
    fileNamePrefix: 'Sentinel_NDVI_' + year,
    fileFormat: 'CSV'
  });
}

// Run manually one year at a time
exportNDVI(2023);