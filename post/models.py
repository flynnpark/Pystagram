from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import re

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    photo = ProcessedImageField(upload_to='post/post/%Y/%m/%d',
                                processors=[ResizeToFill(600, 600)],
                                format='JPEG',
                                options={'quality': 90})
    content = models.CharField(max_length=255, help_text="최대 255자 입력 가능")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tag_set = models.ManyToManyField('Tag', blank=True)
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                            blank=True,
                                            related_name='like_user_set',
                                            through='Like')

    class Meta:
        ordering = ['-created_at']

    # NOTE: content에서 tags를 추출하여 Tag 객체 가져오고, 신규 태그는 Tag instance 생성, 본인의 tag_set에 등록
    def tag_save(self):
        tags = re.findall(r'#(\w+)\b', self.content)

        if not tags:
            return
        for t in tags:
            self.save();
            tag, tag_created = Tag.objects.get_or_create(name=t)
            if not self.tag_set.filter(id=tag.id).exists():
                self.tag_set.add(tag) # NOTE: ManyToManyField에 인스턴스 추가

    def __str__(self):
        return self.content

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    post = models.ForeignKey(Post)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
