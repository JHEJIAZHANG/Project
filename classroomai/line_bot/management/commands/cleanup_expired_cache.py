#!/usr/bin/env python
"""
Django 管理命令：清理過期的作業統計暫存資料

執行方式：
python manage.py cleanup_expired_cache

設定 cron job 自動執行（每小時執行一次）：
0 * * * * cd /path/to/project && python manage.py cleanup_expired_cache
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from line_bot.models import HomeworkStatisticsCache


class Command(BaseCommand):
    help = '清理過期的作業統計暫存資料'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='預覽模式，不實際刪除資料',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='顯示詳細輸出',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write("🧹 開始清理過期的作業統計暫存資料...")
        
        # 找出所有過期的資料
        now = timezone.now()
        expired_cache = HomeworkStatisticsCache.objects.filter(expires_at__lte=now)
        
        total_count = expired_cache.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS("✅ 沒有發現過期的暫存資料")
            )
            return
        
        if verbose or dry_run:
            self.stdout.write(f"📊 發現 {total_count} 筆過期資料：")
            for cache in expired_cache[:10]:  # 只顯示前10筆
                self.stdout.write(
                    f"  - {cache.course_name} / {cache.homework_title} "
                    f"(過期時間: {cache.expires_at}, 教師: {cache.line_user_id})"
                )
            if total_count > 10:
                self.stdout.write(f"  ... 還有 {total_count - 10} 筆資料")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"🔍 預覽模式：將刪除 {total_count} 筆過期資料")
            )
            self.stdout.write("執行實際清理請使用：python manage.py cleanup_expired_cache")
        else:
            # 執行實際清理
            deleted_count, deleted_details = expired_cache.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ 成功清理 {deleted_count} 筆過期的暫存資料"
                )
            )
            
            if verbose:
                self.stdout.write("📋 清理詳情：")
                for model, count in deleted_details.items():
                    if count > 0:
                        self.stdout.write(f"  - {model}: {count} 筆")
        
        # 顯示剩餘有效資料統計
        remaining_count = HomeworkStatisticsCache.objects.filter(expires_at__gt=now).count()
        self.stdout.write(f"📈 剩餘有效暫存資料：{remaining_count} 筆")
        
        if remaining_count > 0:
            # 顯示最近過期的資料
            next_to_expire = HomeworkStatisticsCache.objects.filter(
                expires_at__gt=now
            ).order_by('expires_at').first()
            
            if next_to_expire:
                time_until_expire = next_to_expire.expires_at - now
                hours = int(time_until_expire.total_seconds() // 3600)
                minutes = int((time_until_expire.total_seconds() % 3600) // 60)
                
                self.stdout.write(
                    f"⏰ 下一筆資料將在 {hours}h {minutes}m 後過期"
                )