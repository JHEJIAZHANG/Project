"""
Django 管理命令：創建測試用戶
"""
from django.core.management.base import BaseCommand
from user.models import LineProfile

class Command(BaseCommand):
    help = '創建測試用戶'

    def add_arguments(self, parser):
        parser.add_argument(
            '--line-user-id',
            type=str,
            required=True,
            help='LINE User ID (必須提供)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='測試用戶',
            help='用戶名稱 (預設: 測試用戶)'
        )
        parser.add_argument(
            '--role',
            type=str,
            default='student',
            choices=['student', 'teacher'],
            help='用戶角色 (預設: student)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='用戶郵箱 (預設: test@example.com)'
        )

    def handle(self, *args, **options):
        line_user_id = options['line_user_id']
        name = options['name']
        role = options['role']
        email = options['email']

        # 檢查用戶是否已存在
        user, created = LineProfile.objects.get_or_create(
            line_user_id=line_user_id,
            defaults={
                'name': name,
                'role': role,
                'email': email,
                'extra': {}
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ 成功創建測試用戶: {line_user_id} ({name})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  測試用戶已存在: {line_user_id} ({user.name})')
            )
            
        # 顯示用戶資訊
        self.stdout.write(f'📋 用戶資訊:')
        self.stdout.write(f'   LINE User ID: {user.line_user_id}')
        self.stdout.write(f'   名稱: {user.name}')
        self.stdout.write(f'   角色: {user.role}')
        self.stdout.write(f'   郵箱: {user.email}')