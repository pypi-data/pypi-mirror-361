import os
import tempfile
import geopandas
import shapely
import GeoAnalyze
import pytest


@pytest.fixture(scope='class')
def shape():

    yield GeoAnalyze.Shape()


@pytest.fixture
def point_gdf():

    gdf = GeoAnalyze.core.Core()._geodataframe_point

    return gdf


@pytest.fixture
def message():

    output = {
        'error_driver': 'Could not retrieve driver from the file path.',
        'error_geometry': 'Input shapefile must have geometries of type Polygon.'
    }

    return output


def test_functions(
    shape
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # saving lake shapefile in temporary directory
        transfer_list = GeoAnalyze.File().transfer_by_name(
            src_folder=data_folder,
            dst_folder=tmp_dir,
            file_names=['lake']
        )
        assert 'lake.shp' in transfer_list
        # read lake GeoDataFrame
        lake_file = os.path.join(tmp_dir, 'lake.shp')
        lake_gdf = geopandas.read_file(lake_file)
        # non-decimal whole value float columns to integer columns
        int_gdf = shape.column_nondecimal_float_to_int_type(
            input_file=lake_file,
            output_file=os.path.join(tmp_dir, 'lake.shp')
        )
        assert 'int' in str(int_gdf.dtypes.iloc[-4])
        # adding ID column
        assert 'lid' not in lake_gdf.columns
        id_gdf = shape.column_add_for_id(
            input_file=lake_file,
            column_name='lid',
            output_file=lake_file
        )
        assert 'lid' in id_gdf.columns
        # deleting columns
        assert 'nimi' in lake_gdf.columns
        delete_gdf = shape.column_delete(
            input_file=lake_file,
            column_list=['nimi'],
            output_file=lake_file
        )
        assert 'nimi' not in delete_gdf.columns
        # retaining columns
        retain_gdf = shape.column_retain(
            input_file=lake_file,
            column_list=['lid'],
            output_file=lake_file
        )
        assert list(retain_gdf.columns) == ['lid', 'geometry']
        # unique value of columns
        cuv_dict = shape.column_unique_values(
            shape_file=lake_file
        )
        assert len(cuv_dict) == 1
        assert len(cuv_dict['lid']) == 190
        # new column value mapping
        ncvm_gdf = shape.column_add_mapped_values(
            input_file=lake_file,
            column_exist='lid',
            column_new='nid',
            mapping_value={
                x: 1 if x % 3 == 1 else 2 if x % 3 == 2 else 0 for x in range(1, 191)
            },
            output_file=os.path.join(tmp_dir, 'lake_nid.shp')
        )
        assert 'nid' in ncvm_gdf.columns
        # area by column unique values
        cuva_gdf = shape.column_area_by_value(
            shape_file=os.path.join(tmp_dir, 'lake_nid.shp'),
            column_name='nid',
            csv_file=os.path.join(tmp_dir, 'lake_nid.csv')
        )
        assert len(cuva_gdf) == 3
        # Coordinate Reference System reprojection
        reproject_gdf = shape.crs_reprojection(
            input_file=lake_file,
            target_crs='EPSG:4326',
            output_file=os.path.join(tmp_dir, 'crs_reproject.shp')
        )
        assert str(reproject_gdf.crs) == 'EPSG:4326'
        # rectangular bounding box
        box_gdf = shape.boundary_box(
            input_file=lake_file,
            output_file=os.path.join(tmp_dir, 'box_lake.shp')
        )
        assert len(box_gdf) == 1
        # converting polygons to boundary lines
        shape.polygons_to_boundary_lines(
            input_file=lake_file,
            output_file=os.path.join(tmp_dir, 'line.shp')
        )
        geometry_type = GeoAnalyze.core.Core().shapefile_geometry_type(
            shape_file=os.path.join(tmp_dir, 'line.shp')
        )
        assert geometry_type == 'LineString'
        # polygon filling
        lake_hole = all(lake_gdf.geometry.apply(lambda x: len(list(x.interiors)) == 0))
        assert lake_hole is False
        lakeunion_gdf = geopandas.GeoDataFrame(
            data={'luid': [1], 'geometry': [lake_gdf.union_all()]},
            crs=lake_gdf.crs
        )
        lakeunion_gdf.to_file(os.path.join(tmp_dir, 'lake_union.shp'))
        lakefill_gdf = shape.polygon_fill(
            input_file=os.path.join(tmp_dir, 'lake_union.shp'),
            output_file=os.path.join(tmp_dir, 'lake_union_fill.shp'),
            explode=True
        )
        lake_hole = all(lakefill_gdf.geometry.apply(lambda x: len(list(x.interiors)) == 0))
        assert lake_hole
        # polygon filling after merging
        lake_hole = all(lake_gdf.geometry.apply(lambda x: len(list(x.interiors)) == 0))
        assert lake_hole is False
        lakefill_gdf = shape.polygon_fill_after_merge(
            input_file=lake_file,
            column_name='lid',
            output_file=os.path.join(tmp_dir, 'lake_fill.shp')
        )
        lake_hole = all(lakefill_gdf.geometry.apply(lambda x: len(list(x.interiors)) == 0))
        assert lake_hole
        assert len(lake_gdf) > len(lakefill_gdf)
        # polygon count by cumulative sum percentages of areas
        cumarea_count = shape.polygon_count_by_cumsum_area(
            shape_file=lake_file
        )
        assert len(cumarea_count) == 20
        # removing polygons by cumulative area percentage cutoff
        lakecutoff_gdf = shape.polygons_remove_by_cumsum_area_percent(
            input_file=lake_file,
            percent_cutoff=90,
            output_file=os.path.join(tmp_dir, 'lake_cutoff_90.shp'),
            index_sort=True
        )
        assert len(lakecutoff_gdf) == 10
        # extracting spatial join geometries
        extract_gdf = shape.extract_spatial_join_geometries(
            input_file=lake_file,
            overlay_file=os.path.join(data_folder, 'stream.shp'),
            output_file=os.path.join(tmp_dir, 'lake_extracted.shp')
        )
        assert len(extract_gdf) == 6
        # extracting geometries by overlap threshold
        boundary_gdf = GeoAnalyze.Raster().boundary_polygon(
            raster_file=os.path.join(data_folder, 'dem_mask.tif'),
            shape_file=os.path.join(tmp_dir, 'dem_mask_boundary.shp')
        )
        assert len(boundary_gdf) == 1
        extract_gdf = shape.extract_polygons_by_overlap_threshold(
            input_file=os.path.join(data_folder, 'dem_mask_index.shp'),
            mask_file=os.path.join(tmp_dir, 'dem_mask_boundary.shp'),
            output_file=os.path.join(tmp_dir, 'dem_mask_index_extracted.shp'),
            overlap_percent=50
        )
        assert len(extract_gdf) == 13
        # array from geometries without mask
        output_profile = GeoAnalyze.Raster().array_from_geometries_without_mask(
            shape_file=os.path.join(tmp_dir, 'dem_mask_boundary.shp'),
            value_column='bid',
            resolution=16,
            output_file=os.path.join(tmp_dir, 'dem_mask_boundary.tif')
        )
        assert output_profile['driver'] == 'GTiff'
        assert output_profile['height'] == 3923
        assert output_profile['width'] == 3551
        # error test extracting geometries by overlap threshold
        disconnect_box = shapely.box(
            xmin=boundary_gdf.total_bounds[2] + 1000,
            ymin=boundary_gdf.total_bounds[3] + 1000,
            xmax=boundary_gdf.total_bounds[2] + 1000 + 1000,
            ymax=boundary_gdf.total_bounds[3] + 1000 + 1000
        )
        disconnect_gdf = geopandas.GeoDataFrame(
            geometry=[disconnect_box],
            crs=boundary_gdf.crs
        )
        disconnect_gdf.to_file(os.path.join(tmp_dir, 'mask_disconnect.shp'))
        with pytest.raises(Exception) as exc_info:
            shape.extract_polygons_by_overlap_threshold(
                input_file=os.path.join(data_folder, 'dem_mask_index.shp'),
                mask_file=os.path.join(tmp_dir, 'mask_disconnect.shp'),
                output_file=os.path.join(tmp_dir, 'dem_mask_disconect.shp')
            )
        assert exc_info.value.args[0] == 'No overlapping geometry found'
        # aggregating geometries from shapefile
        with tempfile.TemporaryDirectory() as tmp2_dir:
            lake1_gdf = lake_gdf.iloc[:50, :]
            lake1_gdf.to_file(os.path.join(tmp2_dir, 'lake_1.shp'))
            lake2_gdf = lake_gdf.iloc[-50:, :]
            lake2_gdf.to_file(os.path.join(tmp2_dir, 'lake_2.shp'))
            aggregate_gdf = shape.aggregate_geometries_from_shapefiles(
                folder_path=tmp2_dir,
                geometry_type='Polygon',
                column_name='aid',
                output_file=os.path.join(tmp_dir, 'aggregate.shp')
            )
            assert len(aggregate_gdf) == 100
            # error test for missing Coordinate Reference System
            lake2_gdf = lake2_gdf.set_crs('EPSG:4326', allow_override=True)
            lake2_gdf.to_file(os.path.join(tmp2_dir, 'lake_2.shp'))
            with pytest.raises(Exception) as exc_info:
                shape.aggregate_geometries_from_shapefiles(
                    folder_path=tmp2_dir,
                    geometry_type='Polygon',
                    column_name='aid',
                    output_file=os.path.join(tmp_dir, 'aggregate.shp')
                )
            assert exc_info.value.args[0] == 'Not all shapefiles have the same Coordinate Reference System.'


def test_aggregate_geometries_from_layers(
    shape
):

    # create GeoDataFrame of points for layer 1
    l1p_gdf = geopandas.GeoDataFrame(
        {
            'id': [1, 2],
            'geometry': [
                shapely.Point(102, 0.5),
                shapely.Point(103, 1.0)
            ]
        },
        crs='EPSG:4326'
    )

    # create GeoDataFrame of points for layer 2
    l2p_gdf = geopandas.GeoDataFrame(
        {
            'id': [1, 2],
            'geometry': [
                shapely.Point(104, 0.5),
                shapely.Point(105, 1.0)
            ]
        },
        crs='EPSG:4326'
    )

    # create GeoDataFrame of lines for layer 3
    l3ls_gdf = geopandas.GeoDataFrame(
        {
            'id': [1, 2],
            'geometry': [
                shapely.LineString([(100, 0), (101, 1)]),
                shapely.LineString([(101, 1), (102, 2)])
            ]
        },
        crs='EPSG:4326'
    )

    # create GeoDataFrame of lines for layer 4
    l4ls_gdf = geopandas.GeoDataFrame(
        {
            'id': [1, 2],
            'geometry': [
                shapely.LineString([(102, 2), (103, 3)]),
                shapely.LineString([(103, 3), (104, 4)])
            ]
        },
        crs='EPSG:4326'
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        # saving layers to a GPKG file in temporary directory
        gpkg_file = os.path.join(tmp_dir, 'tmp.gpkg')
        l1p_gdf.to_file(gpkg_file, layer='l1_p')
        l2p_gdf.to_file(gpkg_file, layer='l2_p')
        l3ls_gdf.to_file(gpkg_file, layer='l3_ls')
        l4ls_gdf.to_file(gpkg_file, layer='l4_ls')
        # extracting line layers
        line_gdf = shape.aggregate_geometries_from_layers(
            input_file=gpkg_file,
            geometry_type='LineString',
            output_file=os.path.join(tmp_dir, 'layer_lines.shp'),
            column_list=['id']
        )
        assert line_gdf.shape == (4, 3)
        # error for geometry column
        with pytest.raises(Exception) as exc_info:
            shape.aggregate_geometries_from_layers(
                input_file=gpkg_file,
                geometry_type='LineString',
                output_file=os.path.join(tmp_dir, 'layer_lines.shp'),
                column_list=['id', 'geometry']
            )
        assert exc_info.value.args[0] == 'The column name "geometry" cannot be included in the column_list.'
        # error for layer column
        with pytest.raises(Exception) as exc_info:
            shape.aggregate_geometries_from_layers(
                input_file=gpkg_file,
                geometry_type='LineString',
                output_file=os.path.join(tmp_dir, 'layer_lines.shp'),
                column_list=['id', 'layer']
            )
        assert exc_info.value.args[0] == 'To include "layer" in column_list, the name of the optional variable layer_column must be changed.'
        # error for geometry type
        with pytest.raises(Exception) as exc_info:
            shape.aggregate_geometries_from_layers(
                input_file=gpkg_file,
                geometry_type='Line',
                output_file=os.path.join(tmp_dir, 'layer_lines.shp'),
                column_list=['id']
            )
        assert exc_info.value.args[0] == "Input geometry type must be one of ['Point', 'LineString', 'Polygon']."


def test_error_shapefile_driver(
    shape,
    message
):

    # non-decimal whole value float columns to integer columns
    with pytest.raises(Exception) as exc_info:
        shape.column_nondecimal_float_to_int_type(
            input_file='input.shp',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # retaining columns
    with pytest.raises(Exception) as exc_info:
        shape.column_retain(
            input_file='input.shp',
            column_list=['C1'],
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # deleting columns
    with pytest.raises(Exception) as exc_info:
        shape.column_delete(
            input_file='input.shp',
            column_list=['C1'],
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # adding ID column
    with pytest.raises(Exception) as exc_info:
        shape.column_add_for_id(
            input_file='input.shp',
            column_name=['C1'],
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # new column value mapping
    with pytest.raises(Exception) as exc_info:
        shape.column_add_mapped_values(
            input_file='input.shp',
            column_exist='lid',
            column_new='nid',
            mapping_value={
                x: 1 if x % 3 == 1 else 2 if x % 3 == 2 else 0 for x in range(1, 191)
            },
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # Coordinate Reference System reprojection
    with pytest.raises(Exception) as exc_info:
        shape.crs_reprojection(
            input_file='input.shp',
            target_crs='EPSG:3067',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # rectangular bounding box
    with pytest.raises(Exception) as exc_info:
        shape.boundary_box(
            input_file='input.shp',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # converting polygons to boundary lines
    with pytest.raises(Exception) as exc_info:
        shape.polygons_to_boundary_lines(
            input_file='input.shp',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # polygon filling
    with pytest.raises(Exception) as exc_info:
        shape.polygon_fill(
            input_file='input.shp',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # polygon filling after merge
    with pytest.raises(Exception) as exc_info:
        shape.polygon_fill_after_merge(
            input_file='input.shp',
            column_name='lid',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # removing polygons by cumulative area percentage cutoff
    with pytest.raises(Exception) as exc_info:
        shape.polygons_remove_by_cumsum_area_percent(
            input_file='input.shp',
            percent_cutoff=90,
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # extracting spatial join geometries
    with pytest.raises(Exception) as exc_info:
        shape.extract_spatial_join_geometries(
            input_file='input.shp',
            overlay_file='overlay.shp',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # extracting geometries by overlap threshold
    with pytest.raises(Exception) as exc_info:
        shape.extract_polygons_by_overlap_threshold(
            input_file='dem_mask_index.shp',
            mask_file='dem_mask_boundary.shp',
            output_file='dem_mask_index_extracted.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # aggregating geometries from shapefiles
    with pytest.raises(Exception) as exc_info:
        shape.aggregate_geometries_from_shapefiles(
            folder_path='input_folder',
            geometry_type='Polygon',
            column_name='aid',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']
    # aggregating geometries from layers
    with pytest.raises(Exception) as exc_info:
        shape.aggregate_geometries_from_layers(
            input_file='input_file.gpkg',
            geometry_type='LineString',
            output_file='output.sh'
        )
    assert exc_info.value.args[0] == message['error_driver']


def test_error_geometry(
    shape,
    point_gdf,
    message
):

    with tempfile.TemporaryDirectory() as tmp_dir:
        # saving point GeoDataFrame
        point_file = os.path.join(tmp_dir, 'point.shp')
        point_gdf.to_file(point_file)
        # area by column unique values
        with pytest.raises(Exception) as exc_info:
            shape.column_area_by_value(
                shape_file=point_file,
                column_name='nid',
                csv_file='lake_nid.csv'
            )
        assert exc_info.value.args[0] == message['error_geometry']
        # polygon filling
        with pytest.raises(Exception) as exc_info:
            shape.polygon_fill(
                input_file=point_file,
                output_file='polygon_fill.shp'
            )
        assert exc_info.value.args[0] == message['error_geometry']
        # polygon filling after merge
        with pytest.raises(Exception) as exc_info:
            shape.polygon_fill_after_merge(
                input_file=point_file,
                column_name='lid',
                output_file='polygon_fill.shp'
            )
        assert exc_info.value.args[0] == message['error_geometry']
        # polygon count by cumulative sum percentages of areas
        with pytest.raises(Exception) as exc_info:
            shape.polygon_count_by_cumsum_area(
                shape_file=point_file
            )
        assert exc_info.value.args[0] == message['error_geometry']
        # removing polygons by cumulative area percentage cutoff
        with pytest.raises(Exception) as exc_info:
            shape.polygons_remove_by_cumsum_area_percent(
                input_file=point_file,
                percent_cutoff=90,
                output_file='output.shp'
            )
        assert exc_info.value.args[0] == message['error_geometry']
        # extracting geometries by overlap threshold
        with pytest.raises(Exception) as exc_info:
            shape.extract_polygons_by_overlap_threshold(
                input_file=point_file,
                mask_file='dem_mask_boundary.shp',
                output_file='dem_mask_index_extracted.shp'
            )
        assert exc_info.value.args[0] == message['error_geometry']
