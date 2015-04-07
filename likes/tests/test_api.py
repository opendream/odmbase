
from tastypie.models import ApiKey

from goals.models import Goal, TeamGoal
from odmbase.likes.models import Like
from updates.models import Update

from utilities import factory
from utilities.tests import RedisResourceTestCase


class LikeResourceTest(RedisResourceTestCase):

    def setUp(self):
        super(LikeResourceTest, self).setUp()
        self.taeyeon = factory.create_user()
        self.jessica = factory.create_user()
        self.yoona = factory.create_user()

        self.goal_category = factory.create_goal_category(name='health')
        
        self.goal = factory.create_goal(category=self.goal_category, created_by=self.taeyeon)
        self.team_goal = factory.create_goal(category=self.goal_category, created_by=self.taeyeon, goal_class=TeamGoal)
        self.update = factory.create_update(goal=self.goal, progress=10, created_by=self.taeyeon)

        self.like1 = factory.create_like(dst=self.update, src=self.taeyeon)
        self.like2 = factory.create_like(dst=self.update, src=self.jessica)

    def get_credentials(self, user): 
        api_key = ApiKey.objects.get(user=user)
        return self.create_apikey(username=user.username, api_key=api_key.key)

    def test_post_create_like_with_anonymous_user(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/like/'))

    def test_post_create_like_goal(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.yoona)))

        goal = Goal.objects.get(id=self.goal.id)
        self.assertEqual(goal.id, self.goal.id)
        self.assertEqual(goal.likes_count, 2)

    def test_post_create_like_team_goal(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.team_goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        team_goal = TeamGoal.objects.get(id=self.team_goal.id)
        self.assertEqual(team_goal.id, self.team_goal.id)
        self.assertEqual(team_goal.likes_count, 1)

    def test_post_create_like_update(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.update.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.yoona)))

        update = Update.objects.get(id=self.update.id)
        self.assertEqual(update.id, self.update.id)
        self.assertEqual(update.likes_count, 3)

    def test_post_create_like_same_person(self):
        self.assertHttpBadRequest(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.update.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        self.assertHttpBadRequest(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.update.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        update = Update.objects.get(id=self.update.id)
        self.assertEqual(update.id, self.update.id)
        self.assertEqual(update.likes_count, 2)

    def test_delete_like_update(self):
        self.assertHttpAccepted(self.api_client.delete('/api/v1/like/%d/' % self.like1.id,
            authentication=self.get_credentials(self.taeyeon)))

        update = Update.objects.get(id=self.update.id)
        self.assertEqual(update.id, self.update.id)
        self.assertEqual(update.likes_count, 1)

    def test_post_create_and_delete_like_team_goal(self):
        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.team_goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))

        team_goal = TeamGoal.objects.get(id=self.team_goal.id)
        self.assertEqual(team_goal.likes_count, 1)

        like = Like.objects.latest('id')
        self.assertHttpAccepted(self.api_client.delete('/api/v1/like/%d/' % like.id, 
            authentication=self.get_credentials(self.jessica)))
        team_goal = TeamGoal.objects.get(id=self.team_goal.id)
        self.assertEqual(team_goal.likes_count, 0)

        self.assertHttpCreated(self.api_client.post('/api/v1/like/', format='json', 
            data={
                "dst": "/api/v1/common/%d/" % self.team_goal.commonmodel_ptr.id}, 
            authentication=self.get_credentials(self.jessica)))
        team_goal = TeamGoal.objects.get(id=self.team_goal.id)
        self.assertEqual(team_goal.likes_count, 1)
