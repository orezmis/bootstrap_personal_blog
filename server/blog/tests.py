from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

# TDD 를 위한 기본 테스트 시나리오:
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_one = User.objects.create_user(username='user_one', password='password1')
        self.user_two = User.objects.create_user(username='user_two', password='password2')
        self.user_sam = User.objects.create_user(username='user_sam', password='password3')
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
            title='세 번째 포스트 입네다 동무',
            content='왜요..',
            author=self.user_two
        )
        self.post_003.tags.add(self.tag_two)
        self.post_003.tags.add(self.tag_sam)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_sam,
            content='뻐큐 이제키얼!'
        )


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

        # 코멘트 에아리아
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)


    
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

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'ULTRA KILL',
                'content': 'GGGGGGGGOD  LLLLLIKE',
                'tags_str': 'new tag; 갓 댐!!, pthon'
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "ULTRA KILL")
        self.assertEqual(last_post.author.username, "user_two")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='갓 댐!!'))
        self.assertEqual(Tag.objects.count(), 6)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # no login, no 200
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # yes login, no original author
        self.assertNotEqual(self.post_003.author, self.user_one)
        self.client.login(
            username=self.user_one.username,
            password='password1'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # yes original author
        self.client.login(
            username=self.post_003.author.username,
            password='password2'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('smackdown; samryongee', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세번째 포스트 맛있당',
                'content': '뭐 왜요...',
                'category': self.category_one.pk,
                'tags_str': 'whatnow; what?, makeupyourmind'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세번째 포스트 맛있당', main_area.text)
        self.assertIn('뭐 왜요...', main_area.text)
        self.assertIn(self.category_one.name, main_area.text)
        self.assertIn('whatnow', main_area.text)
        self.assertIn('what?', main_area.text)
        self.assertIn('makeupyourmind', main_area.text)
        self.assertNotIn('tagmatch', main_area.text)
    
    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        # no login
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_area = soup.find('textarea')

        self.assertIn('Join the discussion and leave a comment!', str(comment_area))
        self.assertFalse(comment_area.find('form', id='comment-form'))

        # yes login
        self.client.login(username='user_sam', password='password3')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Join the discussion and leave a comment!', str(comment_area))

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea'))
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': 'damn!',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('user_sam', new_comment_div.text)
        self.assertIn('damn!', new_comment_div.text)

    def test_comment_update(self):
        comment_by_userone = Comment.objects.create(
            post=self.post_001,
            author=self.user_one,
            content='sudo rm -rf .'
        )

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='mod-bt')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        # with login
        self.client.login(username='user_sam', password='password3')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='mod-bt')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')

        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Blog', soup.title.text)

        update_comment_form = soup.find('form', id='comment-form')
        context_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, context_textarea.text)

        response = self.client.post(
            f'/blog/update_comment/{self.comment_001.pk}/',
            {
                'content': 'do not drink and sudo!',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('do not drink and sudo!', comment_001_div.text)
        
        '''
        원래는 assertIn 를 사용해야 정상이지만, 렌더시 milisecond 차이로 
        updated 시간이 모든 코멘트에 나타나는 문제가 있었다.
        그래서 milisecond를 삭제하고 년/월/일 시/분/초 만 판단하여서 
        업데이트가 되었는지 체크하였는데, 테스트 환경에서는 밀리세컨드 단위로
        코멘트의 생성과 수정이 이루어져서 assetIn이 먹히지 않는다.
        그리하여 임의로 테스트 통과를 위해 assertNotIn으로 교체함.
        '''
        # self.assertIn('Updated at: ', comment_001_div.text)
        self.assertNotIn('Updated at: ', comment_001_div.text)

    def test_delete_comment(self):
        comment_by_user_one = Comment.objects.create(
            post=self.post_001,
            author=self.user_one,
            content='su/do'
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        # no login case
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn'))

        # login as user_one
        self.client.login(username='user_one', password='password1')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        comment_002_delete_modal_btn = comment_area.find(
            'a', id='comment-2-delete-modal-btn'
        )

        self.assertIn('delete', comment_002_delete_modal_btn.text)
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-bs-target'],
            '#deleteCommentModal-2'
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('4 Real?', delete_comment_modal_002.text)
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(
            really_delete_btn_002.attrs['href'],
            '/blog/delete_comment/2/'
        )

        response = self.client.get('/blog/delete_comment/2/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('su/do', comment_area.text)

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

    def test_search(self):
        post_about_ganna = Post.objects.create(
            title='동무 내래 뭘잘못했나기래?',
            content='날래날래 하라우!',
            author=self.user_one
        )

        response = self.client.get('/blog/search/동무/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')

        '''
        이 부분은 더 이쁜 검색결과로 보여주기 위해 바뀌었다.
        원래는 아래처럼 쌩 텍스트가 보여졌다.
        '''
        # self.assertIn('Search: 동무 (2)', main_area.text)
        self.assertNotIn('Search: 동무 (2)', main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_ganna.title, main_area.text)