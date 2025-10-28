"""自动生成器 API 路由"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_current_user
from ...db.session import get_session
from ...models.user import User
from ...schemas.auto_generator import (
    AutoGeneratorLogResponse,
    AutoGeneratorTaskResponse,
    CreateAutoGeneratorTaskRequest,
)
from ...services.auto_generator_service import AutoGeneratorService

router = APIRouter(prefix="/api/auto-generator", tags=["auto-generator"])


@router.post("/tasks", response_model=AutoGeneratorTaskResponse)
async def create_auto_generator_task(
    request: CreateAutoGeneratorTaskRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """创建自动生成任务"""
    try:
        task = await AutoGeneratorService.create_task(
            db=db,
            project_id=request.project_id,
            user_id=current_user.id,
            target_chapters=request.target_chapters,
            chapters_per_batch=request.chapters_per_batch,
            interval_seconds=request.interval_seconds,
            auto_select_version=request.auto_select_version,
            generation_config=request.generation_config,
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.post("/tasks/{task_id}/start", response_model=AutoGeneratorTaskResponse)
async def start_auto_generator_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """启动自动生成任务"""
    try:
        # 验证任务所有权
        task = await AutoGeneratorService.get_task(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this task"
            )

        task = await AutoGeneratorService.start_task(db, task_id)
        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start task: {str(e)}"
        )


@router.post("/tasks/{task_id}/pause", response_model=AutoGeneratorTaskResponse)
async def pause_auto_generator_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """暂停自动生成任务"""
    try:
        # 验证任务所有权
        task = await AutoGeneratorService.get_task(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this task"
            )

        task = await AutoGeneratorService.pause_task(db, task_id)
        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause task: {str(e)}"
        )


@router.post("/tasks/{task_id}/stop", response_model=AutoGeneratorTaskResponse)
async def stop_auto_generator_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """停止自动生成任务"""
    try:
        # 验证任务所有权
        task = await AutoGeneratorService.get_task(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this task"
            )

        task = await AutoGeneratorService.stop_task(db, task_id)
        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=AutoGeneratorTaskResponse)
async def get_auto_generator_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """获取自动生成任务详情"""
    task = await AutoGeneratorService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    # 验证任务所有权
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )
    return task


@router.get("/tasks/{task_id}/logs", response_model=List[AutoGeneratorLogResponse])
async def get_auto_generator_logs(
    task_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """获取自动生成任务日志"""
    # 验证任务所有权
    task = await AutoGeneratorService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )

    logs = await AutoGeneratorService.get_task_logs(db, task_id, limit)
    return logs


@router.get("/projects/{project_id}/tasks", response_model=List[AutoGeneratorTaskResponse])
async def get_project_tasks(
    project_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """获取项目的所有自动生成任务"""
    tasks = await AutoGeneratorService.get_project_tasks(db, project_id, current_user.id)
    return tasks
