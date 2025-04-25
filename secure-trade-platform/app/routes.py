from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from app import db, bcrypt, login_manager
from app.models import User, Post, PostReport, UserReport
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, DeleteAccountForm, ChargeWalletForm, CreateProductForm, UpdateEmailForm, UpdatePasswordForm, SearchForm
from app.decorators import admin_required

user_bp = Blueprint('user_bp', __name__)
product_bp = Blueprint('product_bp', __name__)
admin_bp = Blueprint('admin_bp', __name__)

@user_bp.route('/')
def home():
    return render_template('home.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('user_bp.login'))
    return render_template('register.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            if user.username == 'admin':
                return redirect(url_for('user_bp.admin_reports'))
            return redirect(url_for('user_bp.home'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@user_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user_bp.home'))

@user_bp.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, posts=posts)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    email_form = UpdateEmailForm(prefix='email')
    password_form = UpdatePasswordForm(prefix='password')
    delete_form = DeleteAccountForm(prefix='delete')

    if email_form.submit.data and email_form.validate_on_submit():
        current_user.email = email_form.email.data
        db.session.commit()
        flash("Email updated.", 'success')
        return redirect(url_for('user_bp.settings'))

    if password_form.submit.data and password_form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, password_form.current_password.data):
            hashed = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            current_user.password = hashed
            db.session.commit()
            flash("Password updated.", 'success')
        else:
            flash("Current password is incorrect.", 'danger')
        return redirect(url_for('user_bp.settings'))

    if delete_form.submit.data and delete_form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        flash("Account deleted.", 'success')
        return redirect(url_for('user_bp.home'))

    return render_template('settings.html',
                           email_form=email_form,
                           password_form=password_form,
                           delete_form=delete_form)

@user_bp.route('/charge_wallet', methods=['GET', 'POST'])
@login_required
def charge_wallet():
    form = ChargeWalletForm()
    if form.validate_on_submit():
        current_user.balance += form.amount.data
        db.session.commit()
        flash("Wallet charged successfully.", 'success')
        return redirect(url_for('user_bp.profile'))
    return render_template('charge_wallet.html', form=form)

@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    form = CreateProductForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, price=form.price.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Product created!', 'success')
        return redirect(url_for('user_bp.profile'))
    return render_template('create_product.html', form=form)

@product_bp.route('/product/<int:post_id>', methods=['GET'])
@login_required
def product_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('product_detail.html', post=post)

@product_bp.route('/product/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You do not have permission to edit this product.', 'danger')
        return redirect(url_for('user_bp.profile'))
    form = CreateProductForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.price = form.price.data
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('user_bp.profile'))
    return render_template('edit_product.html', form=form, post=post)

@product_bp.route('/product/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_product(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You do not have permission to delete this product.', 'danger')
        return redirect(url_for('user_bp.profile'))
    db.session.delete(post)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('user_bp.profile'))

@product_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == 'POST':
        keyword = form.keyword.data
        sort_by = form.sort_by.data
    else:
        keyword = request.args.get('keyword', '')
        sort_by = request.args.get('sort_by', 'latest')

    # @username 처리
    if keyword.startswith('@'):
        username = keyword[1:]
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('user_bp.view_profile', user_id=user.id))  # ✅ 수정
        else:
            flash('User not found.', 'warning')
            return redirect(url_for('user_bp.home'))
    query = Post.query.filter(Post.title.contains(keyword))
    if sort_by == 'price_asc':
        query = query.order_by(Post.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Post.price.desc())
    else:
        query = query.order_by(Post.date_posted.desc())
    results = query.all()
    return render_template('search_results.html', form=form, results=results, keyword=keyword, sort_by=sort_by)

@product_bp.route('/product/<int:post_id>/buy', methods=['POST'])
@login_required
def buy_product(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id or post.is_sold:
        flash("You cannot buy this product.", 'danger')
        return redirect(url_for('product_bp.product_detail', post_id=post.id))
    post.buyer_id = current_user.id
    db.session.commit()
    flash("Purchase initiated. Please confirm when you receive the item.", 'info')
    return redirect(url_for('product_bp.product_detail', post_id=post.id))

@product_bp.route('/product/<int:post_id>/confirm', methods=['POST'])
@login_required
def confirm_purchase(post_id):
    post = Post.query.get_or_404(post_id)
    if post.buyer_id != current_user.id:
        flash("Only the buyer can confirm the purchase.", 'danger')
        return redirect(url_for('product_bp.product_detail', post_id=post.id))
    post.is_sold = True
    db.session.commit()
    flash("Purchase confirmed. The seller has received the payment.", 'success')
    return redirect(url_for('product_bp.product_detail', post_id=post.id))

@user_bp.route('/delete_account', methods=['POST'], endpoint='delete_account')
@login_required
def delete_account():
    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()  # 로그아웃 처리도 추가
        flash("Your account has been deleted successfully.", 'success')
        return redirect(url_for('user_bp.home'))  # 홈으로 리디렉션
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting your account. Please try again.", 'danger')
        return redirect(url_for('user_bp.profile'))

@user_bp.route('/change_password', methods=['GET', 'POST'], endpoint='change_password')
@login_required
def change_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_pw
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('user_bp.profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('change_password.html', form=form)


@user_bp.route('/report/user/<int:user_id>', methods=['POST'])
@login_required
def report_user(user_id):
    if user_id == current_user.id:
        flash("자기 자신을 신고할 수 없습니다.", 'warning')
        return redirect(url_for('user_bp.profile'))

    # 중복 신고 방지
    existing = UserReport.query.filter_by(reporter_id=current_user.id, reported_user_id=user_id).first()
    if existing:
        flash("이미 신고한 사용자입니다.", 'info')
    else:
        report = UserReport(reporter_id=current_user.id, reported_user_id=user_id)
        db.session.add(report)
        db.session.commit()

        # 자동 제재
        total_reports = UserReport.query.filter_by(reported_user_id=user_id).count()
        if total_reports >= 5:
            user = User.query.get(user_id)
            if user:
                user.is_active = False
                db.session.commit()
                flash("해당 사용자는 누적 신고로 자동 정지되었습니다.", 'danger')
            else:
                flash("해당 사용자를 찾을 수 없습니다.", 'danger')
    return redirect(url_for('user_bp.profile'))


@product_bp.route('/report/post/<int:post_id>', methods=['POST'])
@login_required
def report_post(post_id):
    # 중복 신고 방지
    existing = PostReport.query.filter_by(reporter_id=current_user.id, post_id=post_id).first()
    if existing:
        flash("이미 신고한 게시글입니다.", 'info')
    else:
        report = PostReport(reporter_id=current_user.id, post_id=post_id)
        db.session.add(report)
        db.session.commit()

        # 자동 삭제
        total_reports = PostReport.query.filter_by(post_id=post_id).count()
        if total_reports >= 5:
            post = Post.query.get(post_id)
            if post:
                db.session.delete(post)
                db.session.commit()
                flash("신고 누적으로 게시글이 삭제되었습니다.", 'danger')
            else:
                flash("게시글을 찾을 수 없습니다.", 'danger')
    return redirect(url_for('product_bp.search'))


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user if user and user.is_active else None


@user_bp.route('/profile/<int:user_id>', methods=['GET'], endpoint='view_profile')
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

@user_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


# 관리자 신고 내역 보기
@user_bp.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    user_reports = UserReport.query.all()
    post_reports = PostReport.query.all()
    return render_template('admin_reports.html', user_reports=user_reports, post_reports=post_reports)

# 사용자 계정 정지
@user_bp.route('/admin/suspend_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash("해당 사용자가 정지되었습니다.", "warning")
    return redirect(url_for('user_bp.admin_reports'))

# 게시글 삭제
@user_bp.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("해당 게시글이 삭제되었습니다.", "info")
    return redirect(url_for('user_bp.admin_reports'))

@admin_bp.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    reported_users = UserReport.query.all()
    reported_posts = PostReport.query.all()
    return render_template('admin/reports.html', reported_users=reported_users, reported_posts=reported_posts)


@admin_bp.route('/admin/deactivate_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("관리자 계정은 비활성화할 수 없습니다.", 'danger')
        return redirect(url_for('admin_bp.admin_reports'))
    user.is_active = False
    db.session.commit()
    flash("사용자 계정이 정지되었습니다.", 'warning')
    return redirect(url_for('admin_bp.admin_reports'))


@admin_bp.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("게시글이 삭제되었습니다.", 'info')
    return redirect(url_for('admin_bp.admin_reports'))

@admin_bp.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("관리자는 제재할 수 없습니다.", "danger")
        return redirect(url_for('admin_bp.view_reports'))
    user.is_active = False
    db.session.commit()
    flash(f"사용자 {user.username}가 제재되었습니다.", "warning")
    return redirect(url_for('admin_bp.view_reports'))

