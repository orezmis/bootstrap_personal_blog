from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# TDD 를 위한 기본 테스트 시나리오:
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_one = User.objects.create_user(username='user_one', password='password1')
        self.user_two = User.objects.create_user(username='user_two', password='password2')
        self.category_one = Category.objects.create(name='cat_one', slug='metal')
        self.category_two = Category.objects.create(name='cat_two', slug='slug')

        self.tag_one = Tag.objects.create(name='tagmatch', slug='tagmatch')
        self.tag_two = Tag.objects.create(name='smackdown', slug='smackdown')
        self.tag_sam = Tag.objects.create(name='samryongee', slug='samryongee')

        self.user_two.is_staff = True
        self.user_two.save()

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world!',
            category=self.category_one,
            author=self.user_one
        )
        self.post_001.tags.add(self.tag_one)

        self.post_002 = Post.objects.create(
            title='두번째 포스트',
            content='World, Hello!',
            category=self.category_two,
            author=self.user_two
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트',
            content='왜요..',
            author=self.user_two
        )
        self.post_003.tags.add(self.tag_two)
        self.post_003.tags.add(self.tag_sam)


    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_one.name} ({self.category_one.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_two.name} ({self.category_two.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류', categories_card.text)

    # /blog/ 경로에 접속해서 원하는 페이지가 나오는지 확인하며, 게시물이 잘 쓰여지는지 확인하는 테스트 시나리오
    def test_post_list(self):
        # with posts
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_one.name, post_001_card.text)
        self.assertNotIn(self.tag_two.name, post_001_card.text)
        self.assertNotIn(self.tag_sam.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_one.name, post_002_card.text)
        self.assertNotIn(self.tag_two.name, post_002_card.text)
        self.assertNotIn(self.tag_sam.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.user_one.username.upper(), main_area.text)
        self.assertIn(self.user_two.username.upper(), main_area.text)
        self.assertNotIn(self.tag_one.name, post_003_card.text)
        self.assertIn(self.tag_two.name, post_003_card.text)
        self.assertIn(self.tag_sam.name, post_003_card.text)

        # without post
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)
        

        # DEPRECATED BELOW
        # # 1. 포스트(게시글) 목록 페이지를 가져온다
        # response = self.client.get('/blog/')
        
        # # 1.1. 정상 (200) 인지 확인
        # self.assertEqual(response.status_code, 200)
        
        # # 1.2. bs로 페이지 콘텐츠 parse 후 soup 변수에 저장
        # soup = BeautifulSoup(response.content, 'html.parser')
        
        # # 1.3. 페이지 타이틀이 Blog 인지 테스트
        # self.assertEqual(soup.title.text, 'Blog')

        # # 1.4. 네비게이션 바가 있는지 확인
        # # 1.5. 네비게이션 바에 Blog 문구가 있는지 확인
        # # 1.6 네비게이션 바에 About Me 문구가 있는지 확인
        # self.navbar_test(soup)

        # # 2. 포스트 (게시물)이 하나도 없는지 확인
        # self.assertEqual(Post.objects.count(), 0)
        
        # # 2.1. main-area 를 가진 div를 검색  
        # main_area = soup.find('div', id='main-area')
        
        # # 2.2. main_area의 텍스트가 포스트 (게시물)이 하나도 없을때 나와야 하는 문구인지 체크
        # self.assertIn('아직 게시물이 없습니다', main_area.text)



        # # 3. 포스트 (게시글) 2개 생성
        # # post_001 = Post.objects.create(
        # #     title='첫 번째 포스트입니다.',
        # #     content='Hello world!',
        # #     author=self.user_one
        # # )

        # # post_002 = Post.objects.create(
        # #     title='두번째 포스트',
        # #     content='World, Hello!',
        # #     author=self.user_two
        # # )

        # # 3.1. 위에서 2개 생성한대로 포스트가 2개 생성되었는지 확인
        # self.assertEqual(Post.objects.count(), 2)

        # # 3.2. /blog/ 경로로 재접속 (새로고침)
        # response = self.client.get('/blog/')

        # # 3.3. 리스폰스 200 ok 확인
        # self.assertEqual(response.status_code, 200)

        # # 3.4. bs로 페이지 콘텐츠 다시 parse,
        # soup = BeautifulSoup(response.content, 'html.parser')

        # # 3.5. main-area 를 가진 div를 검색 
        # main_area = soup.find('div', id='main-area')

        # # 3.6. main-area 의 텍스트가 위에서 작성한 게시글들의 title 과 일치하는지 확인
        # self.assertIn(post_001.title, main_area.text)
        # self.assertIn(post_002.title, main_area.text)

        # # 3.7. main-area 의 텍스트가 작성한 게시물이 하나도 없을때 나오는 문구가 아닌지 체크
        # self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # self.assertIn(self.user_one.username.upper(), main_area.text)
        # self.assertIn(self.user_two.username.upper(), main_area.text)


    def test_post_detail(self):

        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world!',
            author=self.user_one
        )

        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1.4. 네비게이션 바가 있는지 확인
        self.navbar_test(soup)

        # 1.5. 카테고리가 있는지 확인
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_one.name, post_area.text)

        self.assertIn(self.user_one.username.upper(), post_area.text)

        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_one.name, post_area.text)
        self.assertNotIn(self.tag_two.name, post_area.text)
        self.assertNotIn(self.tag_sam.name, post_area.text)

    
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='OREZMIS')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_category_page(self):
        response = self.client.get(self.category_one.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
       
        self.assertIn(self.category_one.name, soup.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_one.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_one.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup =BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_one.name, soup.text)


        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_one.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # no login, no response 200!
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # no staff login case
        self.client.login(username='user_one', password='password1')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
        # yes staff login, yes 200
        self.client.login(username='user_two', password='password2')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'ULTRA KILL',
                'content': 'GGGGGGGGOD  LLLLLIKE'
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "ULTRA KILL")
        self.assertEqual(last_post.author.username, "user_two")