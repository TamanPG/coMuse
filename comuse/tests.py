from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from .models import Like, Piece, Bookmark, Comment

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("comuse:home")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        Piece.objects.create(user=self.user, title="test", caption="test tweet")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comuse/home.html")

        pieces = response.context["piece_list"]
        self.assertQuerysetEqual(pieces, Piece.objects.all())


class TestPieceCreateView(TestCase):
    def setUp(self):
        self.url = reverse("comuse:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comuse/create.html")

    def test_success_post(self):
        valid_data = {
            "title": "test",
            "caption": "This is a test.",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_title(self):
        empty_title_data = {"user": self.user, "title": "", "caption": "test"}
        response = self.client.post(self.url, empty_title_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Piece.objects.filter(**empty_title_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["title"])
    
    def test_failure_post_with_empty_caption(self):
        empty_caption_data = {"user": self.user, "title": "test", "caption": ""}
        response = self.client.post(self.url, empty_caption_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Piece.objects.filter(**empty_caption_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["caption"])

    def test_failure_post_with_too_long_title(self):
        long_title_data = {"title": "a" * 51}
        response = self.client.post(self.url, long_title_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Piece.objects.filter(**long_title_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("この値は 50 文字以下でなければなりません( 51 文字になっています)。", form.errors["title"])
    
    def test_failure_post_with_too_long_caption(self):
        long_caption_data = {"caption": "a" * 1001}
        response = self.client.post(self.url, long_caption_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Piece.objects.filter(**long_caption_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("この値は 1000 文字以下でなければなりません( 1001 文字になっています)。", form.errors["caption"])


class TestPieceDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.tweet = Piece.objects.create(user=self.user, title="test", caption="This is a test.")
        self.url = reverse("comuse:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comuse/detail.html")


class TestPieceDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_login(self.user1)
        self.piece1 = Piece.objects.create(user=self.user1, title="test1", caption="post1")
        self.piece2 = Piece.objects.create(user=self.user2, title="test2", caption="post2")
        self.url1 = reverse("comuse:delete", kwargs={"pk": self.piece1.pk})
        self.url2 = reverse("comuse:delete", kwargs={"pk": self.piece2.pk})

    def test_success_post(self):
        response = self.client.post(self.url1)
        self.assertRedirects(response, reverse("comuse:home"), status_code=302, target_status_code=200)
        self.assertEqual(Piece.objects.count(), 1)

    def test_failure_post_with_not_exist_piece(self):
        response = self.client.get(reverse("comuse:delete", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Piece.objects.count(), 2)

    def test_failure_post_with_incorrect_piece(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Piece.objects.count(), 2)


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.post = Piece.objects.create(user=self.user, title="test", caption="This is a test.")
        self.url = reverse("comuse:like", kwargs={"pk": self.post.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(target=self.post, user=self.user).exists())

    def test_failure_post_with_not_exist_piece(self):
        url = reverse("comuse:like", kwargs={"pk": "10"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.exists())

    def test_failure_post_with_liked_piece(self):
        Like.objects.create(target=self.post, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 1)


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.post = Piece.objects.create(user=self.user, title="test", caption="This is a test.")
        Like.objects.create(user=self.user, target=self.post)
        self.url = reverse("comuse:like", kwargs={"pk": self.post.pk})

    def test_success_post(self):
        response = self.client.post(reverse("comuse:unlike", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(user=self.user, target=self.post).exists())

    def test_failure_post_with_not_exist_piece(self):
        response = self.client.post(reverse("comuse:unlike", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Like.objects.count(), 1)

    def test_failure_post_with_unliked_piece(self):
        Like.objects.all().delete()
        response = self.client.post(reverse("comuse:unlike", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(user=self.user, target=self.post).count(), 0)


class TestBookmarkView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.post = Piece.objects.create(user=self.user, title="test", caption="This is a test.")
        self.url = reverse("comuse:bookmark", kwargs={"pk": self.post.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Bookmark.objects.filter(target=self.post, user=self.user).exists())

    def test_failure_post_with_not_exist_piece(self):
        url = reverse("comuse:bookmark", kwargs={"pk": 10})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Bookmark.objects.exists())

    def test_failure_post_with_bookmarked_piece(self):
        Bookmark.objects.create(target=self.post, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bookmark.objects.count(), 1)


class TestDeleteBookmarkView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.post = Piece.objects.create(user=self.user, title="test", caption="This is a test.")
        Bookmark.objects.create(user=self.user, target=self.post)
        self.url = reverse("comuse:bookmark", kwargs={"pk": self.post.pk})

    def test_success_post(self):
        response = self.client.post(reverse("comuse:deleteBookmark", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Bookmark.objects.filter(user=self.user, target=self.post).exists())

    def test_failure_post_with_not_exist_piece(self):
        response = self.client.post(reverse("comuse:deleteBookmark", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_failure_post_with_unbookmarked_piece(self):
        Bookmark.objects.all().delete()
        response = self.client.post(reverse("comuse:deleteBookmark", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Bookmark.objects.filter(user=self.user, target=self.post).count(), 0)


class TestCommentView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.post = Piece.objects.create(user=self.user, title="test", caption="This is a test.", commentAllowance=True)
        self.url = reverse("comuse:comment", kwargs={"pk": self.post.pk})

    def test_success_post(self):
        valid_data = {
            "content": "test",
        }
        response = self.client.post(self.url, valid_data)
        self.assertTrue(Comment.objects.filter(target=self.post, user=self.user).exists())
        self.assertRedirects(
            response,
            reverse("comuse:detail", kwargs={"pk": self.post.pk}),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)


class TestDeleteCommentView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_login(self.user1)
        self.piece = Piece.objects.create(user=self.user1, title="test", caption="post", commentAllowance=True)
        self.comment1 = Comment.objects.create(user=self.user1, content="test", target=self.piece)
        self.comment2 = Comment.objects.create(user=self.user2, content="test2", target=self.piece)
        self.url1 = reverse("comuse:deleteComment", kwargs={"pk": self.piece.pk, "comment_pk": self.comment1.pk})
        self.url2 = reverse("comuse:deleteComment", kwargs={"pk": self.piece.pk, "comment_pk": self.comment2.pk})

    def test_success_post(self):
        response = self.client.post(self.url1)
        self.assertRedirects(response, reverse("comuse:detail", kwargs={"pk": self.piece.pk}), status_code=302, target_status_code=200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_failure_post_with_not_exist_comment(self):
        response = self.client.get(reverse("comuse:deleteComment", kwargs={"pk": self.piece.pk, "comment_pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 2)

    def test_failure_post_with_incorrect_comment(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 2)


class TestSearchView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.piece = Piece.objects.create(user=self.user, title="test", caption="post")
        self.url = reverse("comuse:search")

    def test_matches_both(self):
        response = self.client.get(self.url, {"q": "st"})
        context = response.context
        results = Piece.objects.values_list('title', flat=True)
        cont_list = list(context["piece_list"])
        query_list = list(Piece.objects.select_related("user").prefetch_related("likes", "bookmarks").filter(title__in=results).order_by('-created_at'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comuse/result.html")
        self.assertEqual(cont_list, query_list)
