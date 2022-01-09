
import java.util.*;
import java.net.*;
import java.text.*;
import java.time.LocalDate;
import java.lang.*;
import java.io.*;
import java.sql.*;
import java.sql.Date;
import pgpass.*;

public class CreateQuest {
	private Connection conDB;        // Connection to the database system.
    private String url;              // URL: Which database?
    private String user = "wby225"; // Database user account
    
    private String day;
    private String realm;
    private String theme;
    private int amount;
    private float seed;

    private LocalDate date;
    private LocalDate current_date = LocalDate.now();
    
    public CreateQuest(String[] args) {
    	
    	// setting inputs
        if (args.length < 4 | args.length > 6) {
            // Don't know what's wanted.  Bail.
            System.out.println("\nwrong number of arguments");
            System.exit(0);
        } 
        else {
            try {
            	day   = new String(args[0]);
            	date  = LocalDate.parse(day);
            	realm = new String(args[1]);
            	theme = new String(args[2]);
            	amount = new Integer(args[3]);
            	if (args.length == 5) {
            		user = new String(args[4]);
            	}
            	else if (args.length == 6) {
            		user = new String(args[4]);
            		seed = new Float(args[5]);
            	}
            } catch (NumberFormatException e) {
                System.out.println("\ninvalid inputs");
                System.exit(0);
            }
        }
    	
    	// Set up the DB connection.
        try {
            // Register the driver with DriverManager.
            Class.forName("org.postgresql.Driver").newInstance();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (InstantiationException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (IllegalAccessException e) {
            e.printStackTrace();
            System.exit(0);
        }
        
        // URL: Which database?
        //url = "jdbc:postgresql://db:5432/<dbname>?currentSchema=yrb";
        url = "jdbc:postgresql://db:5432/";
        
        // set up acct info
        // fetch the PASSWD from <.pgpass>
        Properties props = new Properties();
        try {
            String passwd = PgPass.get("db", "*", user, user);
            props.setProperty("user",    user);
            props.setProperty("password", passwd);
            // props.setProperty("ssl","true"); // NOT SUPPORTED on DB
        } catch(PgPassException e) {
            System.out.print("\nCould not obtain PASSWD from <.pgpass>.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Initialize the connection.
        try {
            // Connect with a fall-thru id & password
            //conDB = DriverManager.getConnection(url,"<username>","<password>");
            conDB = DriverManager.getConnection(url, props);
        } catch(SQLException e) {
            System.out.print("\nSQL: database connection error.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Let's have autocommit turned off.  No particular reason here.
        try {
            conDB.setAutoCommit(false);
        } catch(SQLException e) {
            System.out.print("\nFailed trying to turn autocommit off.\n");
            e.printStackTrace();
            System.exit(0);
        }       
        
        // is the seed proper
        if (seed < -1.0 | seed > 1.0) {
        	System.out.print("Seed value ");
        	System.out.print(seed);
        	System.out.println(" is improper.");
        	System.exit(0);
        }
        
        // Is this realm in DB?
        if (!realmCheck()) {
            System.out.print("Realm ");
            System.out.print(realm);
            System.out.println(" does not exist.");
            System.exit(0);
        }
        
        // Is this day in future?
        if (current_date.compareTo(date) >= 0) {
            System.out.print("Day ");
            System.out.print(day);
            System.out.println(" is not in the future.");
            System.exit(0);
        }
        
        // Is the amount exceed what's possible
        if (amountExceed()) {
        	System.out.print("Amount ");
            System.out.print(amount);
            System.out.println(" exceed what is possible.");
            System.exit(0);
        }
        
        if (args.length == 6) {
        	setSeed();
        }
        
        insertQuest();
        insertLoot();
        
        // Commit.  Okay, here nothing to commit really, but why not...
        try {
            conDB.commit();
        } catch(SQLException e) {
            System.out.print("\nFailed trying to commit.\n");
            e.printStackTrace();
            System.exit(0);
        }
        
        // Close the connection.
        try {
            conDB.close();
        } catch(SQLException e) {
            System.out.print("\nFailed trying to close the connection.\n");
            e.printStackTrace();
            System.exit(0);
        }
        
    }
    
    public void setSeed() {
    	String            queryText = "";     // The SQL text.
        PreparedStatement querySt   = null;   // The query handle.
        
        queryText =
                "SELECT setseed(?)";
        
        // Prepare the query.
        try {
            querySt = conDB.prepareStatement(queryText);
        } catch(SQLException e) {
            System.out.println("SQL setSeed() failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Execute the query.
        try {
        	querySt.setFloat(1, seed);
            querySt.executeQuery();
        } catch(SQLException e) {
            System.out.println("SQL setSeed failed in execute");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // We're done with the handle.
        try {
            querySt.close();
        } catch(SQLException e) {
            System.out.print("SQL setSeed failed closing the handle.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
    }
    
    public boolean amountExceed() {
    	String            queryText = "";     // The SQL text.
        PreparedStatement querySt   = null;   // The query handle.
        ResultSet         answers   = null;   // A cursor.
        int total = 0;
        boolean result = false;
        queryText =
                "SELECT sum(sql) "
              + "FROM treasure   ";
        
        // Prepare the query.
        try {
            querySt = conDB.prepareStatement(queryText);
        } catch(SQLException e) {
            System.out.println("SQL amountExceed() failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Execute the query.
        try {
            answers = querySt.executeQuery();
        } catch(SQLException e) {
            System.out.println("SQL amountExceed() failed in execute");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // get total
        try {
        	if (answers.next()) {
        		total = answers.getInt("sum");
                if (amount > total) {
                    result = true;
                } else {
                    result = false;
                }
        	}
        } catch(SQLException e) {
            System.out.println("SQL amountExceed() failed in cursor.");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Close the cursor.
        try {
            answers.close();
        } catch(SQLException e) {
            System.out.print("SQL amountExceed() failed closing cursor.\n");
            System.out.println(e.toString());
            System.exit(0);
        }

        // We're done with the handle.
        try {
            querySt.close();
        } catch(SQLException e) {
            System.out.print("SQL amountExceed() failed closing the handle.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        return result;
    }
    
    public boolean realmCheck() {
    	String            queryText = "";     // The SQL text.
        PreparedStatement querySt   = null;   // The query handle.
        ResultSet         answers   = null;   // A cursor.

        boolean           inDB      = false;  // Return.
        
        queryText =
                "SELECT *       "
              + "FROM Realm     "
              + "WHERE realm = ?";
        
        // Prepare the query.
        try {
            querySt = conDB.prepareStatement(queryText);
        } catch(SQLException e) {
            System.out.println("SQL realmCheck() failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Execute the query.
        try {
            querySt.setString(1, realm);
            answers = querySt.executeQuery();
        } catch(SQLException e) {
            System.out.println("SQL realmCheck() failed in execute");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Any answer?
        try {
            if (answers.next()) {
                inDB = true;
            } else {
                inDB = false;
            }
        } catch(SQLException e) {
            System.out.println("SQL realmCheck() failed in cursor.");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Close the cursor.
        try {
            answers.close();
        } catch(SQLException e) {
            System.out.print("SQL realmCheck() failed closing cursor.\n");
            System.out.println(e.toString());
            System.exit(0);
        }

        // We're done with the handle.
        try {
            querySt.close();
        } catch(SQLException e) {
            System.out.print("SQL realmCheck() failed closing the handle.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        return inDB;
    }
    
    public void insertQuest(){
    	String            queryText = "";     // The SQL text.
        PreparedStatement querySt   = null;   // The query handle.
        
        queryText =
                "INSERT into quest(theme, realm, day) values "
              + "(?, ?, ?)                                   ";
        
        // Prepare the query.
        try {
            querySt = conDB.prepareStatement(queryText);
        } catch(SQLException e) {
            System.out.println("SQL insertQuest() failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }

        // Execute the query.
        try {
            querySt.setString(1, theme);
            querySt.setString(2, realm);
            querySt.setDate(3, Date.valueOf(day));
            querySt.executeUpdate();
        } catch(SQLException e) {
            System.out.println("SQL insertQuest() failed in execute");
            System.out.println(e.toString());
            System.exit(0);
        }

        // We're done with the handle.
        try {
            querySt.close();
        } catch(SQLException e) {
            System.out.print("SQL insertQuest() failed closing the handle.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
    }
    
    public void insertLoot() {
    	String            insertLootText = "";     // The SQL text to insert into Loot
        PreparedStatement insertLootSt   = null;   // The query 'insert into Loot' handle.
        
        String            maxIdText = "";     // The SQL text to get max id.
        PreparedStatement maxIdSt   = null;   // The query to get max id handle.  
        ResultSet         maxIdAnswers   = null;   // A cursor of getting max id.
        
        String            selectTreasureText = "";     // The SQL text to select random treasure.
        PreparedStatement selectTreasureSt   = null;   // The query selecting random treasure handle.
        ResultSet         selectTreasureAnswers   = null;   // A cursor to get random treasure.
        
        int max_id = 0;
        int value = 0;
        String treasure = "";
        
        insertLootText =
        		"INSERT into loot(loot_id, treasure, theme, realm, day) values "
        	  + "(?, ?, ?, ?, ?)                                               ";
        maxIdText = 
        		"SELECT max(loot_id) as loot_id                            "
        	  + "FROM loot                                                 "
        	  + "WHERE treasure = ? and theme = ? and realm = ? and day = ?";
        selectTreasureText = 
        		"SELECT *         "
        	  + "FROM treasure    "
        	  + "ORDER BY random()";
        
        // Prepare first query.
        try {
        	insertLootSt = conDB.prepareStatement(insertLootText);
        } catch(SQLException e) {
            System.out.println("SQL insertLoot failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Prepare second query.
        try {
        	maxIdSt = conDB.prepareStatement(maxIdText);
        } catch(SQLException e) {
            System.out.println("SQL maxId failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Prepare third query.
        try {
        	selectTreasureSt = conDB.prepareStatement(selectTreasureText);
        } catch(SQLException e) {
            System.out.println("SQL selectTreasure failed in prepare");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        // Execute third query.
        try {
        	selectTreasureAnswers = selectTreasureSt.executeQuery();
        } catch(SQLException e) {
            System.out.println("SQL selectTreasure failed in execute");
            System.out.println(e.toString());
            System.exit(0);
        }
        
        while(value < amount) {
        	try {
        		if (selectTreasureAnswers.next()) {
        			treasure = selectTreasureAnswers.getString("treasure");
            		value += selectTreasureAnswers.getInt("sql");
            		maxIdSt.setString(1, treasure);
            		maxIdSt.setString(2, theme);
            		maxIdSt.setString(3, realm);
            		maxIdSt.setDate(4, Date.valueOf(day));
            		maxIdAnswers = maxIdSt.executeQuery();
            		maxIdAnswers.next();
            		max_id = maxIdAnswers.getInt("loot_id") + 1;
            		insertLootSt.setInt(1, max_id);
            		insertLootSt.setString(2, treasure);
            		insertLootSt.setString(3, theme);
            		insertLootSt.setString(4, realm);
            		insertLootSt.setDate(5, Date.valueOf(day));
            		insertLootSt.executeUpdate();
        		}
        	}catch(SQLException e) {
        		System.out.println("while loop failed");
                System.out.println(e.toString());
                System.exit(0);
        	}     	
        };
        
        // Close the cursor.
        try {
        	maxIdAnswers.close();
        	selectTreasureAnswers.close();
        } catch(SQLException e) {
            System.out.print("SQL insertLoot() failed closing cursor.\n");
            System.out.println(e.toString());
            System.exit(0);
        }

        // We're done with the handle.
        try {
        	insertLootSt.close();
        	maxIdSt.close();
        	selectTreasureSt.close();
        } catch(SQLException e) {
            System.out.print("SQL insertLoot() failed closing the handle.\n");
            System.out.println(e.toString());
            System.exit(0);
        }
    }
    
    public static void main(String[] args) {
        CreateQuest ct = new CreateQuest(args);
    }
}
