from bs4 import BeautifulSoup
from app.modules.dataset.services import DSMetaDataService,CommentService
import re


def test_create_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= list(s.find("div",class_="comments-container").div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Hola', "The comment content is incorrect"
def test_no_content_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'','parent_id':None})
    assert response.status_code==400
def test_create_comment_no_login(test_database_poblated):
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    assert response.status_code==302, "The user should get redirected if not logged in"
    redirect_url = response.headers.get('Location').split('?')[0]
    assert redirect_url == '/login', "The user should get redirected to log in page"
def test_create_parent_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    id=int(s.find("div",class_="comments-container").div["id"].split("-")[1])
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Adios','parent_id':id})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= s.find("div",id=re.compile(r'children-\d+'))
    assert comment!=None, "The comment is not created as a response"
    comment=list(comment.div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Adios', "The comment content is incorrect"
