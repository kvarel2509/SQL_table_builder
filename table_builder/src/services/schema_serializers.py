from rest_framework import serializers

from table_builder.src.owns.schema import ColumnSchema, TableSchema


class ColumnSchemaSerializer(serializers.Serializer):
	name = serializers.CharField()
	data_type = serializers.CharField()

	def create(self, validated_data):
		return ColumnSchema(**validated_data)


class TableSchemaSerializer(serializers.Serializer):
	pk = serializers.IntegerField(required=False, allow_null=True)
	name = serializers.CharField()
	db_pk = serializers.IntegerField()
	column_schemes = ColumnSchemaSerializer(required=False, many=True)

	def create(self, validated_data):
		return TableSchema(
			pk=validated_data.get('pk'),
			name=validated_data.get('name'),
			db_pk=validated_data.get('db_pk'),
			column_schemes=[ColumnSchema(**column_schema) for column_schema in validated_data.get('column_schemes')]
		)
