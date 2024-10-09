from sqlalchemy.orm import Session
from sqlalchemy import exists
from fastapi import HTTPException, Body
from src.resources.comment.model import Comments, MetaComments
from src.resources.user.model import User
from src.resources.posts.model import Posts
import uuid
from datetime import datetime, timezone


# Comments on a post
def make_comment(db: Session, post_id: str, userid: str, data: str = Body()):
    try:
        post = db.query(Posts).filter(Posts.id == post_id).one_or_none()
        if not post or post.is_deleted:
            raise HTTPException(status_code=404, detail="No post found!")
        data = Comments(
            id=str(uuid.uuid4()),
            userid=userid,
            postid=post_id,
            data=data,
            created_at=datetime.now(tz=timezone.utc),
        )

        db.add(data)
        post.comments += 1
        db.commit()
        db.refresh(data)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_all_comments_of_post(db: Session, postid: str, pageno: int, limit: int):
    pageno = pageno * limit - limit
    try:
        post = db.query(Posts).filter(Posts.id == postid).one_or_none()
        if not post or post.is_deleted:
            raise HTTPException(status_code=404, detail="No post found!")
        data = (
            db.query(Comments)
            .filter(Comments.postid == postid)
            .offset(pageno)
            .limit(limit)
            .all()
        )
        if len(data) == 0 and pageno == 0:
            raise HTTPException(status_code=404, detail="No comments yet!")
        res = []
        for i in data:
            if not i.is_deleted :
                comm_id = i.id
                meta_comment = db.query(MetaComments).filter(MetaComments.commentid==comm_id).all()
                res.append(i)
                for j in meta_comment:
                    if not j.is_deleted:
                        res.append({"userid":i.userid,"data":j.data,"created_at":j.created_at})
        return res
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_single_comment_by_id(db: Session, postid: str, comment_id: str):
    try:
        is_post = db.query(exists().where(Comments.postid == postid)).scalar()
        if not is_post:
            raise HTTPException(
                status_code=404,
                detail="Invalid post-id! No comments on this post exist!",
            )

        data = (
            db.query(Comments)
            .filter(Comments.postid == postid, Comments.id == comment_id)
            .one_or_none()
        )
        if data is None:
            raise HTTPException(status_code=404, detail="No such comment on the post!")
        if data.is_deleted:
            raise HTTPException(status_code=404, detail="No such comments exist!")
        return data
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_all_comments_of_a_user(db: Session, userid: str, pageno: int, limit: int):
    pageno = pageno * limit - limit
    try:
        data = (
            db.query(Comments)
            .filter(Comments.userid == userid)
            .offset(pageno)
            .limit(limit)
            .all()
        )
        if len(data) == 0 and pageno == 0:
            raise HTTPException(status_code=404, detail="NO comments yet!")
        res = []
        for i in data:
            if not i.is_deleted:
                res.append(i)
        return res
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def delete_comment(db: Session, post_id: str, comment_id: str, current_userid: str):
    try:

        is_post = db.query(exists().where(Comments.postid == post_id)).scalar()
        if not is_post:
            raise HTTPException(
                status_code=404,
                detail="Invalid post-id! No comments on this post exist!",
            )

        is_comment = db.query(exists().where(Comments.id == comment_id)).scalar()
        if not is_comment:
            raise HTTPException(status_code=404, detail="No such comment on post")

        commenter_id = (    
            db.query(Comments).filter(Comments.id == comment_id).one_or_none()
        )
        post_owner_id = db.query(Posts).filter(Posts.id == post_id).one_or_none()

        if (
            commenter_id.userid == current_userid
            or post_owner_id.user_id == current_userid
        ):
            data = db.query(Comments).filter(Comments.id == comment_id).one_or_none()
            if data.is_deleted:
                raise HTTPException(status_code=404, detail="No comments exist!")
            data.is_deleted = True
            post = db.query(Posts).filter(Posts.id == post_id).one_or_none()
            post.comments -= 1
            db.commit()
            return True
        else:
            raise HTTPException(
                status_code=401, detail="Can not delete other's comment!"
            )

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


# Meta comments of a comment
def make_meta_comment(
    db: Session, userid: str, post_id: str, commentid: str, data: str
):
    try:
        is_post = db.query(Posts).filter(Posts.id == commentid).one_or_none()
        if not is_post or is_post.is_deleted:
            raise HTTPException(status_code=404, detail="No post found!")

        comment = db.query(Comments).filter(Comments.id == commentid).one_or_none()
        if not comment or comment.is_deleted:
            raise HTTPException(status_code=404, detail="No such comment on the post !")

        data = MetaComments(
            id=str(uuid.uuid4()),
            commentid=commentid,
            userid=userid,
            data=data,
            created_at=datetime.now(tz=timezone.utc),
        )

        db.add(data)
        comment.replies += 1
        db.commit()
        db.refresh(data)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def delete_meta_comment(
    db: Session,
    post_id: str,
    comment_id: str,
    meta_comment_id: str,
    current_userid: str,
):
    try:

        is_comment = db.query(exists().where(Comments.id == comment_id)).scalar()
        if not is_comment:
            raise HTTPException(
                status_code=404, detail="Invalid comment-id! No such comments exist!"
            )

        is_metacomment = db.query(
            exists().where(MetaComments.id == meta_comment_id)
        ).scalar()
        if not is_metacomment:
            raise HTTPException(status_code=404, detail="No such reply on the comment")

        commenter_id = (
            db.query(MetaComments)
            .filter(MetaComments.id == meta_comment_id)
            .one_or_none()
        )
        post_owner_id = db.query(Posts).filter(Posts.id == post_id).one_or_none()

        if (
            commenter_id.userid == current_userid
            or post_owner_id.user_id == current_userid
        ):
            data = (
                db.query(MetaComments)
                .filter(MetaComments.id == meta_comment_id)
                .one_or_none()
            )
            if data.is_deleted:
                raise HTTPException(status_code=404, detail="No comments exist!")
            data.is_deleted = True
            comment = db.query(Comments).filter(Comments.id == comment_id).one_or_none()
            comment.replies -= 1
            db.commit()
            return True
        else:
            raise HTTPException(
                status_code=401, detail="Can not delete other's comment!"
            )

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_single_meta_comment_by_id(db: Session, comment_id: str, meta_comment_id: str):
    try:
        is_comment = db.query(exists().where(Comments.id == comment_id)).scalar()
        if not is_comment:
            raise HTTPException(
                status_code=404,
                detail="Invalid post-id! No comments on this post exist!",
            )

        data = (
            db.query(MetaComments)
            .filter(
                MetaComments.id == meta_comment_id, MetaComments.commentid == comment_id
            )
            .one_or_none()
        )
        if data is None:
            raise HTTPException(status_code=404, detail="No such comment on the post!")
        if data.is_deleted:
            raise HTTPException(status_code=404, detail="No such comments exist!")
        return data
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

# def get_all_meta_comments_of_comment(db: Session, commentid: str, pageno: int, limit: int):
#     pageno = pageno * limit - limit
#     try:
#         # breakpoint()
#         comment = db.query(Comments).filter(Comments.id == commentid).one_or_none()
#         if not comment or comment.is_deleted:
#             raise HTTPException(status_code=404, detail="No Comments found!")
#         data = (
#             db.query(MetaComments)
#             .filter(MetaComments.commentid ==commentid )
#             .offset(pageno)
#             .limit(limit)
#             .all()
#         )
#         if len(data) == 0 and pageno == 0:
#             raise HTTPException(status_code=404, detail="No meta comments!")
#         res = []
#         for i in data:
#             if not i.is_deleted:
#                 res.append(i)
#         return res
#     except Exception as err:
#         print(str(err))
#         raise HTTPException(status_code=500, detail=str(err))