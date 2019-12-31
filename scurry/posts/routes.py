from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from scurry import db
from scurry.models import Post, User
from scurry.posts.forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route('/post', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    return render_template('post.html', title="Create Post", form=form)

@posts.route('/underground', methods=['GET', 'POST'])
@login_required
def underground():
    postForm = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(private=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('underground.html', title="Underground Feed", postForm=postForm, posts=posts)

@posts.route('/burrow', methods=['GET', 'POST'])
@login_required
def burrow():
    postForm = PostForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('burrow.html', postForm=postForm, title="My Burrow", posts=posts)

@posts.route('/like/<int:post_id>/<action>')  
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)



@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
 
@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        flash('Post has been updated', 'success')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('post.html', title='Update post', 
                            form=form)


@posts.route('/post/<int:post_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been Deleted', 'success')
    return redirect(url_for('main.index'))


