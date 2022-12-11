from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# TDD 를 위한 기본 테스트 시나리오:
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
    
    # /blog/ 경로에 접속해서 원하는 페이지가 나오는지 확인하며, 게시물이 잘 쓰여지는지 확인하는 테스트 시나리오
    def test_post_list(self):
        # 1. 포스트(게시글) 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        
        # 1.1. 정상 (200) 인지 확인
        self.assertEqual(response.status_code, 200)
        
        # 1.2. bs로 페이지 콘텐츠 parse 후 soup 변수에 저장
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1.3. 페이지 타이틀이 Blog 인지 테스트
        self.assertEqual(soup.title.text, 'Blog')

        # 1.4. 네비게이션 바가 있는지 확인
        navbar = soup.nav

        # 1.5. 네비게이션 바에 Blog 문구가 있는지 확인
        self.assertIn('Blog', navbar.text)

        # 1.6 네비게이션 바에 About Me 문구가 있는지 확인
        self.assertIn('About Me', navbar.text)



        # 2. 포스트 (게시물)이 하나도 없는지 확인
        self.assertEqual(Post.objects.count(), 0)
        
        # 2.1. main-area 를 가진 div를 검색  
        main_area = soup.find('div', id='main-area')
        
        # 2.2. main_area의 텍스트가 포스트 (게시물)이 하나도 없을때 나와야 하는 문구인지 체크
        self.assertIn('아직 게시물이 없습니다', main_area.text)



        # 3. 포스트 (게시글) 2개 생성
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world!'
        )

        post_002 = Post.objects.create(
            title='두번째 포스트',
            content='World, Hello!'
        )

        # 3.1. 위에서 2개 생성한대로 포스트가 2개 생성되었는지 확인
        self.assertEqual(Post.objects.count(), 2)

        # 3.2. /blog/ 경로로 재접속 (새로고침)
        response = self.client.get('/blog/')

        # 3.3. 리스폰스 200 ok 확인
        self.assertEqual(response.status_code, 200)

        # 3.4. bs로 페이지 콘텐츠 다시 parse,
        soup = BeautifulSoup(response.content, 'html.parser')

        # 3.5. main-area 를 가진 div를 검색 
        main_area = soup.find('div', id='main-area')

        # 3.6. main-area 의 텍스트가 위에서 작성한 게시글들의 title 과 일치하는지 확인
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)

        # 3.7. main-area 의 텍스트가 작성한 게시물이 하나도 없을때 나오는 문구가 아닌지 체크
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)


    def test_post_detail(self):

        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world!'
        )

        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1.4. 네비게이션 바가 있는지 확인
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        self.assertIn(post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)

        # author test 작성은 다음에..

        self.assertIn(post_001.content, post_area.text)
