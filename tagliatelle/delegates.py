"""Module Defining Default Delegates and Delegate Related Classes"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from penne.messages import Message
    from penne.core import Client

from penne import Delegate, inject_methods, inject_signals
import moderngl_window as mglw


class MethodDelegate(Delegate):
    """Delegate representing a method which can be invoked on the server

    Attributes:
        _client (client object): 
            client delegate is a part of 
        info (message): 
            message containing information on the method
        specifier (str): 
            keyword for specifying the type of delegate
        context_map (dict):
            mapping specifier to context for method invocation
    """

    def __init__(self, client: Client, message: Message, specifier: str):
        self._client = client
        self.info = message
        self.specifier = specifier
        self.context_map = {
            "tables": "table",
            "plots": "plot",
            "entities": "entity"
        }

    def on_new(self, message: Message):
        pass

    def on_remove(self, message: Message):
        pass

    def invoke(self, on_delegate: Delegate, args=None, callback=None):
        """Invoke this delegate's method

        Args:
            on_delegate (delegate):
                delegate method is being invoked on 
                used to get context
            args (list, optional):
                args for the method
            callback (function):
                function to be called when complete
        """
        context = {self.context_map[on_delegate.specifier]: on_delegate.info.id}
        self._client.invoke_method(self.info.id, args, context=context, on_done=callback)


    def __repr__(self) -> str:
        """Custom string representation for methods"""
        
        rep = f"{self.info.name}:\n\t{self.info.doc}\n\tReturns: {self.info.return_doc}\n\tArgs:"
        for arg in self.info.arg_doc:
            rep += f"\n\t\t{arg.name}: {arg.doc}"
        return rep


class SignalDelegate(Delegate):
    """Delegate representing a signal coming from the server

    Attributes:
        _client (Client): 
            client delegate is a part of 
        info (message): 
            message containing information on the signal
        specifier (str): 
            keyword for specifying the type of delegate
    """
    
    def __init__(self, client: Client, message: Message, specifier: str):
        self._client = client
        self.info = message
        self.specifier = specifier

    def on_new(self, message: Message):
        pass

    def on_remove(self, message: Message): 
        pass


class SelectionRange(tuple):
    """Selection of range of rows"""

    def __new__(cls, key_from: int, key_to: int):
        return super().__new__(SelectionRange, (key_from, key_to))


class Selection(object):
    """Selection of certain rows in a table

    Attributes:
        name (str): 
            name of the selection
        rows (list[int]): 
            list of indices of rows
        row_ranges (list[SelectionRange]): 
            ranges of selected rows
    """

    def __init__(self, name: str, rows: list[int] = None, row_ranges: list[SelectionRange] = None):
        self.name = name
        self.rows = rows
        self.row_ranges = row_ranges

    def __repr__(self) -> str:
        return f"Selection Object({self.__dict__})"

    def __getitem__(self, attribute):
        return getattr(self, attribute)


class TableDelegate(Delegate):
    """Delegate representing a table

    Each table delegate corresponds with a table on the server
    To use the table, you must first subscribe 

    Attributes:
        _client (Client): 
            weak ref to client to invoke methods and such
        dataframe (Dataframe): 
            dataframe representing current state of the table
        selections (dict): 
            mapping of name to selection object
        signals (signals): 
            mapping of signal name to function
        name (str): 
            name of the table
        id (list): 
            id group for delegate in state and table on server
    """

    def __init__(self, client: Client, message: Message, specifier: str):
        super().__init__(client, message, specifier)
        self.name = "Table Delegate"
        self.selections = {}
        self.signals = {
            "tbl_reset" : self._reset_table,
            "tbl_rows_removed" : self._remove_rows,
            "tbl_updated" : self._update_rows,
            "tbl_selection_updated" : self._update_selection
        }
        # Specify public methods 
        self.__all__ = [
            "subscribe", 
            "request_clear", 
            "request_insert", 
            "request_remove", 
            "request_update", 
            "request_update_selection",
            "plot"
        ]


    def _on_table_init(self, init_info: Message, on_done=None):
        """Creates table from server response info

        Args:
            init_info (Message Obj): 
                Server response to subscribe which has columns, keys, data, 
                and possibly selections
        """

        # Extract data from init info and transpose rows to cols
        row_data = getattr(init_info, "data")
        cols = getattr(init_info, "columns")
        print(f"Table Initialized with cols: {cols} and row data: {row_data}")


    def _reset_table(self):
        """Reset dataframe and selections to blank objects

        Method is linked to 'tbl_reset' signal
        """

        self.selections = {}


    def _remove_rows(self, key_list: list[int]):
        """Removes rows from table

        Method is linked to 'tbl_rows_removed' signal

        Args:
            key_list (list): list of keys corresponding to rows to be removed
        """

        print(f"Removed Rows: {key_list}...\n", self.dataframe)



    def _update_rows(self, keys: list[int], rows: list):
        """Update rows in table

        Method is linked to 'tbl_updated' signal

        Args:
            keys (list): 
                list of keys to update
            cols (list): 
                list of cols containing the values for each new row,
                should be col for each col in table, and value for each key
        """

        print(f"Updated Rows...{keys}\n")
        

    def _update_selection(self, selection_obj: Selection):
        """Change selection in delegate's state to new selection object

        Method is linked to 'tbl_selection_updated' signal

        Args:
            selection_obj (Selection): 
                obj with new selections to replace obj with same name
        """

        self.selections[selection_obj.name] = selection_obj
        print(f"Made selection {selection_obj.name} = {selection_obj}")


    def _relink_signals(self):
        """Relink the signals for built in methods

        These should always be linked, along with whatever is injected,
        so relink on new and on update messages
        """

        self.signals["noo::tbl_reset"] = self._reset_table
        self.signals["noo::tbl_rows_removed"] = self._remove_rows
        self.signals["noo::tbl_updated"] = self._update_rows
        self.signals["noo::tbl_selection_updated"] = self._update_selection


    def on_new(self, message: Message):
        """Handler when create message is received

        Args:
            message (Message): create message with the table's info
        """
        
        # Set name
        name = message["name"]
        methods = message["methods_list"]
        signals = message["signals_list"]
        if name: self.name = name
    
        # Inject methods and signals
        if methods: inject_methods(self, methods)
        if signals: inject_signals(self, signals)

        # Reset
        self._reset_table()
        self._relink_signals()


    def on_update(self, message: Message):
        """Handler when update message is received
        
        Args:
            message (Message): update message with the new table's info
        """

        self._relink_signals()
    

    def on_remove(self, message: Message):
        pass


    def subscribe(self, on_done: Callable=None):
        """Subscribe to this delegate's table

        Calls on_table_init as callback
        
        Raises:
            Exception: Could not subscribe to table
        """

        try:
            # Allow for calback after table init
            lam = lambda data: self._on_table_init(data, on_done)
            self.tbl_subscribe(on_done=lam)
        except:
            raise Exception("Could not subscribe to table")

    
    def request_insert(self, row_list: list[list[int]], on_done=None):
        """Add rows to end of table

        User endpoint for interacting with table and invoking method
        For input, row list is list of rows. Also note that tables have
        nine columns by default (x, y, z, r, g, b, sx, sy, sz).
        x, y, z -> coordinates
        r, g, b -> color values [0, 1]
        sx, sy, sz -> scaling factors, default size is 1 meter

        Row_list: [[1, 2, 3, 4, 5, 6, 7, 8, 9]]

        Args:
            col_list (list, optional): add rows as list of columns
            row_list (list, optional): add rows using list of rows
            on_done (function, optional): callback function
        Raises:
            Invalid input for request insert exception
        """

        self.tbl_insert(on_done, row_list)
    

    def request_update(self, keys:list[int], rows:list[list[int]], on_done=None):
        """Update the table using a DataFrame

        User endpoint for interacting with table and invoking method

        Args:
            data_frame (DataFrame):
                data frame containing the values to be updated
            on_done (function, optional): 
                callback function called when complete
        """
        
        self.tbl_update(on_done, keys, rows)


    def request_remove(self, keys: list[int], on_done=None):
        """Remove rows from table by their keys

        User endpoint for interacting with table and invoking method

        Args:
            keys (list):
                list of keys for rows to be removed
            on_done (function, optional): 
                callback function called when complete
        """

        self.tbl_remove(on_done, keys)


    def request_clear(self, on_done=None):
        """Clear the table

        User endpoint for interacting with table and invoking method

        Args:
            on_done (function, optional): callback function called when complete
        """
        self.tbl_clear(on_done)


    def request_update_selection(self, name: str, keys: list[int], on_done=None):
        """Update a selection object in the table

        User endpoint for interacting with table and invoking method

        Args:
            name (str):
                name of the selection object to be updated
            keys (list):
                list of keys to be in new selection
            on_done (function, optional): 
                callback function called when complete
        """

        self.tbl_update_selection(on_done, name, {"rows": keys})


class DocumentDelegate(Delegate):
    pass
    
class EntityDelegate(Delegate):

    def __init__(self, client: Client, message: Message, specifier: str):
        super().__init__(client, message, specifier)
        self.name = "No-Name Entity" if not hasattr(self.info, "name") else self.info.name

    def render_entity(self, window):
        
        # Prepare Mesh
        scene = window.scene
        render_rep = self.info.render_rep
        geometry = self.client.state["geometries"][render_rep.mesh].info
        instances = render_rep.instances if hasattr(render_rep, "instances") else None
        patch = geometry.patches[0] # Fragile?

        noodle_material = self.client.state["materials"][patch.material].info
        material = mglw.scene.Material()
        attributes = patch.attributes
        
        view = self.client.state["bufferviews"][patch.attributes[0]["view"]].info
        buffer = self.client.state["buffers"][view.source_buffer].info
        vbo = window.ctx.buffer(buffer.inline_bytes)
        vao = window.ctx.simple_vertex_array(window.prog, vbo, 'vert')
        
        mesh = mglw.scene.Mesh(f"{self.name} Mesh", vao=vao, material=material, attributes=attributes)
        
        # Add mesh as new node to scene graph
        root = scene.find_node("Root")
        root.add_child(mglw.scene.Node(self.name, mesh=mesh))
    
    def on_new(self, message: Message):
        if hasattr(self.info, "render_rep"):
            self.client.callback_queue.put((self.render_entity, []))

class PlotDelegate(Delegate):
    pass

class MaterialDelegate(Delegate):
    pass

class GeometryDelegate(Delegate):
    pass

class LightDelegate(Delegate):
    pass

class ImageDelegate(Delegate):
    pass

class TextureDelegate(Delegate):
    pass

class SamplerDelegate(Delegate):
    pass

class BufferDelegate(Delegate):
    pass

class BufferViewDelegate(Delegate):
    pass
