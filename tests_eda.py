import os
import configparser
import boto3
import pytest
import httpx
from pytest_httpx import HTTPXMock

"""Config Parser to read region, bucket and credentials """
config = configparser.ConfigParser()
config.read("check.ini")

region = config['DEFAULT']['region']
bucket = config['DEFAULT']['bucket']
usrname = config['credentials']['ack']
secret = config['credentials']['sck']

"""URLs and responses for mock"""


catalog_url = 'https://teda.com/catalog'
product_url = 'https://teda.com/product'
complete_json = {"status": "complete"}
product_json = {"inputid": '0001', "name": "WeatherImg-True-North"}
catalog_file = 'catalog_data.csv'
product_file = 'products_sales.csv'

""" S3 boto3 uploader """


@pytest.fixture
def s3_helper():
    """Uplaoder for multiple files"""

    def _uploader(filename):
        src_path = os.path.join(os.getcwd(), filename )
        bclient = boto3.client(
            's3',
            aws_access_key_id=usrname,
            aws_secret_access_key=secret
        )
        bclient.upload_file(src_path, bucket, filename)
        response = bclient.list_objects_v2(Bucket=bucket, Prefix=filename)
        return response
    return _uploader


@pytest.mark.parametrize("files_to_upload", [catalog_file, product_file])
@pytest.mark.uploader
def test_s3_uploader(s3_helper, files_to_upload):
    assert 'Contents' in s3_helper(files_to_upload)


@pytest.mark.catalog
def test_fetch_catalog_ingesting(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=204, text="ingesting")

    with httpx.Client() as client:
        resp = client.get(catalog_url)
        assert resp.status_code == 204
        assert resp.text == "ingesting"


@pytest.mark.catalog
@pytest.mark.dependency()
def test_fetch_catalog_complete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json=complete_json)

    with httpx.Client() as client:
        resp = client.get(catalog_url)
        assert resp.status_code == 200
        assert resp.json() == complete_json


@pytest.mark.catalog
def test_fetch_catalog_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404)

    with httpx.Client() as client:
        resp = client.get(catalog_url)
        assert resp.status_code == 404


@pytest.mark.catalog
@pytest.mark.parametrize("teda_url", [catalog_url, product_url])
def test_fetch_catalog_products_exception_raising(httpx_mock: HTTPXMock, teda_url):
    httpx_mock.add_exception(httpx.ReadTimeout("Read timeout failure"))

    with httpx.Client() as client:
        with pytest.raises(httpx.ReadTimeout):
            client.get(teda_url)


@pytest.mark.common
@pytest.mark.parametrize("teda_url", [catalog_url, product_url])
def test_fetch_catalog_products_timeout(httpx_mock: HTTPXMock, teda_url):
    with httpx.Client() as client:
        with pytest.raises(httpx.TimeoutException):
            client.get(teda_url)


@pytest.mark.product
@pytest.mark.dependency(depends=["test_fetch_catalog_complete"])
def test_fetch_product_complete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json=product_json)

    with httpx.Client() as client:
        resp = client.get(catalog_url)
        assert resp.status_code == 200
        assert resp.json() == product_json
