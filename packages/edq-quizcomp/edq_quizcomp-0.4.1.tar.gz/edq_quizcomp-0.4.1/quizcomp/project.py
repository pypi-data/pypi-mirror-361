import glob
import os

import quizcomp.common
import quizcomp.constants
import quizcomp.question.base
import quizcomp.quiz
import quizcomp.util.dirent
import quizcomp.util.serial

class Project(quizcomp.util.serial.JSONSerializer):
    """
    A project object represents a directory that may contain quizzes and questions.
    The directory (or any file structure) is never serialized.
    """

    def __init__(self, type = quizcomp.constants.TYPE_PROJECT,
            name = '',
            base_dir = '',
            **kwargs):
        super().__init__(type = type, **kwargs)

        self.name = name
        self._base_dir = base_dir

        try:
            self.validate(cls = Project, **kwargs)
        except Exception as ex:
            raise quizcomp.common.QuizValidationError("Error while validating project '%s' ('%s')." % (self._base_dir, self.base_dir)) from ex

    def _validate(self, **kwargs):
        if ((self._base_dir is None) or (self._base_dir == "")):
            raise quizcomp.common.QuizValidationError("Base directory cannot be empty.")

        if (not os.path.isdir(self._base_dir)):
            raise quizcomp.common.QuizValidationError("Base directory '%s' does not exist or is not a directory." % (self._base_dir))

    def find_resources(self):
        """
        Find all the resources associated with this project.
        Returns the path to these resources as (quizzes, questions).
        """

        quizzes = sorted(glob.glob(os.path.join(self._base_dir, '**', quizcomp.constants.QUIZ_FILENAME), recursive = True))
        questions = sorted(glob.glob(os.path.join(self._base_dir, '**', quizcomp.constants.QUESTION_FILENAME), recursive = True))

        return (quizzes, questions)

    def load_resources(self, **kwargs):
        """
        Load (and validate) all the resources associated with this project.
        Returns: ([(quiz path, quiz object), ...], [(question path, question object), ...])
        """

        quiz_paths, question_paths = self.find_resources()

        quizzes = [(path, quizcomp.quiz.Quiz.from_path(path, **kwargs)) for path in quiz_paths]
        questions = [(path, quizcomp.question.base.Question.from_path(path, **kwargs)) for path in question_paths]

        return (quizzes, questions)

    def save(self, out_dir = None):
        """
        Save this project to the specified dir,
        or our own base dir if no other dir is specified.

        Note that in the case we are saving to our own base dir,
        this operation just (re)writes the project file.
        """

        if (out_dir is None):
            out_dir = self._base_dir
        out_dir = os.path.abspath(out_dir)

        if (os.path.isfile(out_dir)):
            raise ValueError("Output for project save cannot be a file, it must be a directory.")

        # If we are pointing to the base_dir, then just save the project file and return.
        if (os.path.isfile(out_dir) and os.path.samefile(out_dir, self._base_dir)):
            self.to_path(os.path.join(self._base_dir, quizcomp.constants.PROJECT_FILENAME))
            return

        quizcomp.util.dirent.copy_dirent(self._base_dir, out_dir,
                symlinks = True, dirs_exist_ok = True)
        self.to_path(os.path.join(out_dir, quizcomp.constants.PROJECT_FILENAME))

    @classmethod
    def from_path(cls, path, **kwargs):
        # If we are looking at a dir, assume the project file is directly inside.
        if (os.path.isdir(path)):
            path = os.path.join(path, quizcomp.constants.PROJECT_FILENAME)

        path = os.path.abspath(path)

        # If the project file does not exist, then continue with minimal info.
        if (not os.path.exists(path)):
            return Project(base_dir = os.path.dirname(path), **kwargs)

        return super().from_path(path, **kwargs)
