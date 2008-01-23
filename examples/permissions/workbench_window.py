"""The workbench window for the permissions framework example."""


# Enthought library imports.
from enthought.pyface.action.api import Action, Group, MenuManager
from enthought.pyface.workbench.api import EditorManager, WorkbenchWindow
from enthought.pyface.workbench.api import Perspective, PerspectiveItem
from enthought.pyface.workbench.action.api import MenuBarManager
from enthought.pyface.workbench.action.api import ToolBarManager
from enthought.pyface.workbench.action.api import ViewMenuManager
from enthought.permissions.api import PermissionsManager, SecureProxy
from enthought.permissions.action.api import LoginAction, LogoutAction
from enthought.traits.api import Callable, HasTraits, List, Instance

# Local imports.
from permissions import NewPersonPerm
from person import Person
from toolkit_editor import ToolkitEditor


class ExampleEditorManager(EditorManager):
    """An editor manager that supports the editor memento protocol."""
    
    #######################################################################
    # 'IEditorManager' interface.
    #######################################################################

    def create_editor(self, window, obj, kind):
        """Reimplemented to create an editor appropriate to the object being
        edited.
        """

        if isinstance(obj, HasTraits):
            # The superclass handles Traits objects.
            editor = super(ExampleEditorManager, self).create_editor(window, obj, kind)
        else:
            # Assume it is handled by a toolkit specific editor.
            editor = ToolkitEditor(window=window, obj=obj)

        return editor


class ExampleWorkbenchWindow(WorkbenchWindow):
    """A simple example of using the workbench window."""

    #### 'WorkbenchWindow' interface ##########################################

    # The available perspectives.
    perspectives = [
        Perspective(
            name     = 'Foo',
            contents = [
                PerspectiveItem(id='Black', position='bottom'),
                PerspectiveItem(id='Debug', position='left')
            ]
        ),
        
        Perspective(
            name     = 'Bar',
            contents = [
                PerspectiveItem(id='Debug', position='left')
            ]
        )
    ]

    #### 'ExampleWorkbenchWindow' interface ###################################

    # The view factories.
    #
    # fixme: This should be part of the standard 'WorkbenchWindow'!
    view_factories = List(Callable)

    #### Private interface ####################################################

    # The Exit action.
    _exit_action = Instance(Action)

    # The New Person action.
    _new_person_action = Instance(Action)

    ###########################################################################
    # 'ApplicationWindow' interface.
    ###########################################################################

    def _editor_manager_default(self):
        """ Trait initializer.

        Here we return the replacement editor manager.
        """

        return ExampleEditorManager()
    
    def _menu_bar_manager_default(self):
        """Trait initializer."""

        file_menu = MenuManager(self._new_person_action, self._exit_action,
                name='&File', id='FileMenu')
        view_menu = ViewMenuManager(name='&View', id='ViewMenu', window=self)

        # Put them in a group so we can optionally append (because the PyFace
        # API doesn't do what you expect with append()).
        group = Group(LoginAction(), LogoutAction())

        for act in PermissionsManager.user_manager.user_actions:
            group.append(act)
        
        for act in PermissionsManager.user_manager.management_actions:
            group.append(act)
        
        for act in PermissionsManager.policy_manager.management_actions:
            group.append(act)
        
        user_menu = MenuManager(group, name='&User', id='UserMenu', window=self)

        return MenuBarManager(file_menu, view_menu, user_menu, window=self)

    def _tool_bar_manager_default(self):
        """Trait initializer."""

        return ToolBarManager(self._exit_action, show_tool_names=False)

    ###########################################################################
    # 'WorkbenchWindow' interface.
    ###########################################################################

    def _views_default(self):
        """Trait initializer."""

        # Using an initializer makes sure that every window instance gets its
        # own view instances (which is necessary since each view has a
        # reference to its toolkit-specific control etc.).
        return [factory(window=self) for factory in self.view_factories]

    ###########################################################################
    # 'ExampleWorkbenchWindow' interface.
    ###########################################################################

    def _view_factories_default(self):
        """Trait initializer."""

        from enthought.pyface.workbench.debug.api import DebugView
        
        return [DebugView]
    
    ###########################################################################
    # Private interface.
    ###########################################################################

    def __exit_action_default(self):
        """Trait initializer."""

        return Action(name='E&xit', on_perform=self.workbench.exit)

    def __new_person_action_default(self):
        """Trait initializer."""
        
        # Create the action and secure it with the appropriate permission.
        act = Action(name='New Person', on_perform=self._new_person)
        act = SecureProxy(act, perms=[NewPersonPerm])

        return act

    def _new_person(self):
        """Create a new person."""

        self.workbench.edit(Person(name='New', age=100))

#### EOF ######################################################################
