
from tastypie.models import ApiKey

from goals.models import Goal, TeamGoal
from updates.models import Update

from utilities import factory
from utilities.tests import RedisResourceTestCase


class CommentResourceTest(RedisResourceTestCase):

    def setUp(self):
        super(CommentResourceTest, self).setUp()
        self.taeyeon = factory.create_user()
        self.jessica = factory.create_user()
        self.yoona = factory.create_user()

        self.goal_category = factory.create_goal_category(name='health')
        
        self.goal = factory.create_goal(category=self.goal_category, created_by=self.taeyeon)
        self.team_goal = factory.create_goal(category=self.goal_category, created_by=self.taeyeon, goal_class=TeamGoal)
        self.update = factory.create_update(goal=self.goal, progress=10, created_by=self.taeyeon)

        self.comment1 = factory.create_comment(dst=self.update, src=self.taeyeon)
        self.comment2 = factory.create_comment(dst=self.update, src=self.jessica)

    def get_credentials(self, user): 
        api_key = ApiKey.objects.get(user=user)
        return self.create_apikey(username=user.username, api_key=api_key.key)

    def test_post_create_comment_with_anonymous_user(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/comment/'))

    def test_post_create_comment_goal(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/comment/', format='json', 
            data={
                "comment": "hello",
                "dst": "/api/v1/common/%d/" % self.goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        self.assertHttpCreated(self.api_client.post('/api/v1/comment/', format='json', 
            data={
                "comment": "hello",
                "dst": "/api/v1/common/%d/" % self.goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.yoona)))

        goal = Goal.objects.get(id=self.goal.id)
        self.assertEqual(goal.id, self.goal.id)
        self.assertEqual(goal.comments_count, 2)

    def test_post_create_comment_team_goal(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/comment/', format='json', 
            data={
                "comment": "hello",
                "dst": "/api/v1/common/%d/" % self.team_goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        team_goal = TeamGoal.objects.get(id=self.team_goal.id)
        self.assertEqual(team_goal.id, self.team_goal.id)
        self.assertEqual(team_goal.comments_count, 1)

    def test_post_create_comment_update(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/comment/', format='json', 
            data={
                "comment": "hello",
                "dst": "/api/v1/common/%d/" % self.update.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.yoona)))

        update = Update.objects.get(id=self.update.id)
        self.assertEqual(update.id, self.update.id)
        self.assertEqual(update.comments_count, 3)

    def test_delete_comment_update(self):
        self.assertHttpAccepted(self.api_client.delete('/api/v1/comment/%d/' % self.comment1.id,
            format='json', authentication=self.get_credentials(self.taeyeon)))

        update = Update.objects.get(id=self.update.id)
        self.assertEqual(update.id, self.update.id)
        self.assertEqual(update.comments_count, 1)
