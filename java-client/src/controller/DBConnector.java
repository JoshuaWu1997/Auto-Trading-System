package controller;

import org.apache.commons.io.FileUtils;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.ResultSet;

public class DBConnector {
    private Connection conn;
    public Statement stmt;
    public ResultSet rs;
    private String DBName, UserName, Password, Host, Port;

    public DBConnector(String dbName, String username, String password) throws IOException {
        this.DBName = dbName;
        this.UserName = username;
        this.Password = password;
        String[] host_port = FileUtils.readFileToString(new File("setting.txt"), "utf-8").split(",");
        Host = host_port[0];
        Port = host_port[1];
        try {
            getConnection();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void getConnection() {
        String driver = "com.mysql.cj.jdbc.Driver";
        String url = "jdbc:mysql://" + Host + ":" + Port + "/" + DBName + "?serverTimezone=GMT%2B8";
        try {
            Class.forName(driver);
            conn = DriverManager.getConnection(url, UserName, Password);
            // System.out.print("successfully connected");
        } catch (SQLException ex) {
            // handle any errors
            System.out.println("SQLException: " + ex.getMessage());
            System.out.println("SQLState: " + ex.getSQLState());
            System.out.println("VendorError: " + ex.getErrorCode());
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    public void executeQuery(String sql) throws Exception {
        if (conn == null) {
            throw new Exception("No databases connected.");
        } else {
            try {
                stmt = conn.createStatement();
                rs = stmt.executeQuery(sql);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}